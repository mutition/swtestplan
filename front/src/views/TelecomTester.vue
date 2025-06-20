<script setup>
import { ref } from 'vue';
import { ElButton, ElTable, ElTableColumn, ElAlert, ElRow, ElCol, ElStatistic, ElInput, ElIcon } from 'element-plus';
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue';

const testResults = ref([]);
const summary = ref(null);
const isLoading = ref(false);
const error = ref('');
const testType = ref('bva'); // bva, equivalence, decision, or custom

// Equivalence class description visibility
const showEquiv = ref(true);
const toggleEquiv = () => { showEquiv.value = !showEquiv.value; };

// Custom test state
const customCallMinutes = ref('');
const customLatePayments = ref('');
const customExpectedFee = ref('');
const customResults = ref([]);
const customTestIdCounter = ref(1);
const customLoading = ref(false);

const runTests = async (type) => {
  testType.value = type;
  error.value = '';
  if (type !== 'custom') {
    isLoading.value = true;
    testResults.value = [];
    summary.value = null;
    try {
      const response = await fetch(`http://127.0.0.1:5000/run-telecom-tests?type=${type}`);
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ message: '无法解析错误响应' }));
        throw new Error(`HTTP 错误！状态: ${response.status}. ${errData.message || ''}`);
      }
      const data = await response.json();
      // Ensure the 'passed' field is a boolean for consistent rendering
      testResults.value = data.results.map(r => ({...r, passed: !!r.passed}));
      summary.value = data.summary;
    } catch (e) {
      error.value = `获取测试数据失败: ${e.message}`;
    } finally {
      isLoading.value = false;
    }
  } else {
    // When switching to custom, clear the pre-set test results but keep custom history
    summary.value = null;
    testResults.value = [];
  }
};

const runCustomTest = async () => {
  customLoading.value = true;
  error.value = '';
  try {
    const response = await fetch('http://127.0.0.1:5000/run-telecom-custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        call_minutes: customCallMinutes.value,
        late_payments: customLatePayments.value,
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '请求失败');
    
    const isPassFailApplicable = customExpectedFee.value !== '';
    let passed = false;
    if (isPassFailApplicable) {
        // Only consider pass if backend did not return an error
        if (!data.error) {
            // Use == for type-agnostic comparison, as input is string
            passed = data.output_fee == customExpectedFee.value;
        }
    }

    const newResult = {
      id: `Custom-${customTestIdCounter.value++}`,
      call_minutes: customCallMinutes.value,
      late_payments: customLatePayments.value,
      expected_fee: customExpectedFee.value === '' ? 'N/A' : Number(customExpectedFee.value),
      output_fee: data.error ? data.output_fee : Number(data.output_fee).toFixed(2),
      description: '自定义测试用例',
      is_pass_fail_applicable: isPassFailApplicable,
      passed: passed,
    };
    customResults.value.unshift(newResult);

    // Clear inputs
    customCallMinutes.value = '';
    customLatePayments.value = '';
    customExpectedFee.value = '';

  } catch (e) {
    error.value = '自定义测试失败: ' + e.message;
  } finally {
    customLoading.value = false;
  }
};

// Initial load
runTests('bva');
</script>

<template>
  <div class="tester-container">
    <div class="actions-bar">
      <el-button type="primary" :plain="testType !== 'bva'" @click="runTests('bva')" size="large">边界值测试</el-button>
      <el-button type="primary" :plain="testType !== 'equivalence'" @click="runTests('equivalence')" size="large">等价类测试</el-button>
      <el-button type="primary" :plain="testType !== 'decision'" @click="runTests('decision')" size="large">决策表测试</el-button>
      <el-button type="primary" :plain="testType !== 'custom'" @click="runTests('custom')" size="large">自定义测试</el-button>
    </div>

    <div v-if="testType === 'equivalence'" class="equiv-desc">
       <div class="equiv-title" style="display:flex;align-items:center;justify-content:space-between;">
        <span>等价类划分依据：</span>
        <el-button size="small" @click="toggleEquiv" circle style="margin-left:10px;">
          <el-icon v-if="showEquiv"><ArrowUp /></el-icon>
          <el-icon v-else><ArrowDown /></el-icon>
        </el-button>
      </div>
      <transition name="fade">
        <ul v-show="showEquiv" class="equiv-list">
            <li><strong>本月通话分钟数 (A)</strong>
              <ul style="padding-left: 20px; margin-top: 5px;">
                  <li><b>A1</b>: (0, 60]</li>
                  <li><b>A2</b>: (60, 120]</li>
                  <li><b>A3</b>: (120, 180]</li>
                  <li><b>A4</b>: (180, 300]</li>
                  <li><b>A5</b>: (300, +∞)</li>
              </ul>
            </li>
            <li style="margin-top: 1em;"><strong>本年度未按时还款次数 (B)</strong>
                <ul style="padding-left: 20px; margin-top: 5px;">
                    <li><b>B1</b>: [0, 1]</li>
                    <li><b>B2</b>: [2]</li>
                    <li><b>B3</b>: [3]</li>
                    <li><b>B4</b>: [4, 5, 6]</li>
                    <li><b>B5</b>: [大于6]</li>
                </ul>
            </li>
        </ul>
      </transition>
    </div>

    <div v-if="testType === 'custom'" class="custom-test-panel">
      <div class="custom-inputs">
        <el-input v-model.number="customCallMinutes" type="number" placeholder="通话分钟数" />
        <el-input v-model.number="customLatePayments" type="number" placeholder="欠费次数" />
        <el-input v-model.number="customExpectedFee" type="number" placeholder="预期总费用" />
        <el-button type="primary" :loading="customLoading" @click="runCustomTest" style="padding: 0 28px;">执行测试</el-button>
      </div>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" :closable="false" />
    
    <div class="content-wrapper">
        <transition name="fade" mode="out-in">
            <div v-if="isLoading" class="loading-state">
                <div class="spinner"></div>
                <p>正在从服务器获取测试结果...</p>
            </div>
            
            <!-- Custom test results table -->
            <div v-else-if="testType === 'custom' && customResults.length > 0" class="results-table">
              <el-table :data="customResults" stripe style="width: 100%" border class="el-table">
                <el-table-column prop="id" label="编号" width="120" />
                <el-table-column label="输入(分钟, 欠费)" width="180">
                  <template #default="scope">
                    <span class="input-mono">({{ scope.row.call_minutes }}, {{ scope.row.late_payments }})</span>
                  </template>
                </el-table-column>
                <el-table-column prop="expected_fee" label="预期总费用" min-width="150" />
                <el-table-column prop="output_fee" label="实际总费用" min-width="150" />
                <el-table-column label="结果" width="100" align="center">
                  <template #default="scope">
                    <span v-if="!scope.row.is_pass_fail_applicable">N/A</span>
                    <span v-else :class="scope.row.passed ? 'table-result-pass' : 'table-result-fail'">
                      {{ scope.row.passed ? '通过' : '失败' }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <!-- Pre-set test results table -->
            <div v-else-if="summary" class="summary-and-results">
                <div class="summary-container">
                     <el-row :gutter="20">
                        <el-col :span="8"><div class="statistic-card"><el-statistic title="总用例数" :value="summary.totalCount" /></div></el-col>
                        <el-col :span="8"><div class="statistic-card pass"><el-statistic title="通过用例" :value="summary.passCount" /></div></el-col>
                        <el-col :span="8"><div class="statistic-card fail"><el-statistic title="失败用例" :value="summary.totalCount - summary.passCount" /></div></el-col>
                    </el-row>
                </div>

                <div class="results-table">
                  <el-table :data="testResults" stripe style="width: 100%" border class="el-table">
                    <el-table-column prop="id" label="编号" width="100" />
                    <el-table-column label="输入(分钟, 欠费)" width="180">
                      <template #default="scope">
                        <span class="input-mono">({{ scope.row.call_minutes }}, {{ scope.row.late_payments }})</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="description" label="用例说明" min-width="220" />
                    <el-table-column prop="expected" label="预期总费用" min-width="150" />
                    <el-table-column prop="output_fee" label="实际总费用" min-width="150" />
                    <el-table-column label="结果" width="100" align="center">
                      <template #default="scope">
                          <span :class="scope.row.passed ? 'table-result-pass' : 'table-result-fail'">
                            {{ scope.row.passed ? '通过' : '失败' }}
                          </span>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
            </div>

            <!-- Empty state -->
            <div v-else-if="!isLoading && !error" class="empty-state">
              <p>请选择一个测试类型开始</p>
            </div>
        </transition>
    </div>

  </div>
</template>

<style scoped>
/* Using a consistent style across all tester components */
.tester-container { max-width: 1300px; margin: 0 auto; }
.actions-bar { text-align: center; margin-bottom: 32px; display: flex; justify-content: center; gap: 16px; }
.el-button { font-weight: 600; padding: 20px 30px; font-size: 1.1rem; }
.error-alert { margin-bottom: 24px; }
.summary-container { margin-bottom: 32px; }
.statistic-card { background-color: var(--color-bg-card); border-radius: var(--border-radius); padding: 20px; box-shadow: var(--shadow); text-align: center; }
.statistic-card.pass { border-left: 5px solid var(--color-success); }
.statistic-card.fail { border-left: 5px solid var(--color-danger); }
.results-table { border: 1px solid var(--color-border); border-radius: var(--border-radius); overflow: hidden; box-shadow: var(--shadow); }
.results-table :deep(.el-table__cell) { text-align: center; }
.content-wrapper { min-height: 400px; display: flex; justify-content: center; align-items: flex-start; width: 100%; }
.loading-state, .empty-state { text-align: center; color: var(--color-text-light); display: flex; flex-direction: column; align-items: center; gap: 16px; margin-top: 100px; }
.spinner { border: 4px solid rgba(0, 0, 0, 0.1); width: 36px; height: 36px; border-radius: 50%; border-left-color: var(--color-primary); animation: spin 1s ease infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.custom-test-panel { padding: 28px; background: #fdfdff; border: 1px solid #e8eaf2; border-radius: 16px; box-shadow: 0 4px 16px rgba(100,100,150,0.05); margin: 0 auto 32px auto; max-width: fit-content; }
.custom-inputs { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; justify-content: center; }
.custom-inputs .el-input { width: 150px; }
.input-mono { font-family: 'JetBrains Mono', 'Fira Mono', 'Consolas', monospace; }
.table-result-pass { color: var(--color-success); font-weight: bold; }
.table-result-fail { color: var(--color-danger); font-weight: bold; }

/* Styles for equivalence description box, aligned with TriangleTester */
.equiv-desc {
  background-color: #f7f9fc;
  border: 1px solid #e4e7ed;
  padding: 20px 24px;
  margin-bottom: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.equiv-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}
.equiv-list {
  padding-left: 20px;
  color: #555;
  line-height: 1.9;
}
.equiv-list li {
  margin-bottom: 10px;
}
.equiv-list b {
  color: #303133;
  background-color: #e9eaec;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 8px;
  font-family: 'JetBrains Mono', 'Fira Mono', 'Consolas', monospace;
}
.equiv-list strong {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
}
</style> 