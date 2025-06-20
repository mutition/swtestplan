<script setup>
import { ref } from 'vue';
import { ElButton, ElTable, ElTableColumn, ElAlert, ElRow, ElCol, ElStatistic, ElInput } from 'element-plus';

const testResults = ref([]);
const summary = ref(null);
const isLoading = ref(false);
const error = ref('');
const testType = ref('bva'); // bva or custom

// Custom test state
const customSales = ref('');
const customWorkHours = ref('');
const customLeaves = ref('');
const customLevel = ref('');
const customExpected = ref('');
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
      // Use the evaluation endpoint
      const response = await fetch(`http://127.0.0.1:5000/run-evaluation-tests`);
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ message: '无法解析错误响应' }));
        throw new Error(`HTTP 错误！状态: ${response.status}. ${errData.message || ''}`);
      }
      const data = await response.json();
      testResults.value = data.results;
      summary.value = data.summary;
    } catch (e) {
      error.value = `获取测试数据失败: ${e.message}`;
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  } else {
    summary.value = null;
    testResults.value = [];
  }
};

const runCustomTest = async () => {
  customLoading.value = true;
  error.value = '';
  try {
    const response = await fetch('http://127.0.0.1:5000/run-evaluation-custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sales: customSales.value || 0,
        work_hours: customWorkHours.value || 0,
        leaves: customLeaves.value || 0,
        level: customLevel.value || 0,
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '请求失败');
    
    const newResult = {
      id: `Custom-${customTestIdCounter.value++}`,
      sales: data.sales,
      work_hours: data.work_hours,
      leaves: data.leaves,
      level: data.level,
      expected: customExpected.value === '' ? 'N/A' : Number(customExpected.value),
      output_score: data.output_score,
      description: '自定义测试用例',
    };
    customResults.value.unshift(newResult);

    // Clear inputs
    customSales.value = '';
    customWorkHours.value = '';
    customLeaves.value = '';
    customLevel.value = '';
    customExpected.value = '';

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
      <el-button
        type="primary"
        :plain="testType !== 'bva'"
        @click="runTests('bva')"
        size="large"
      >
        边界值测试
      </el-button>
      <el-button
        type="primary"
        :plain="testType !== 'custom'"
        @click="runTests('custom')"
        size="large"
      >
        自定义测试
      </el-button>
    </div>

    <div v-if="testType === 'custom'" class="custom-test-panel">
      <div class="custom-inputs">
        <el-input v-model.number="customSales" type="number" placeholder="销售额" style="width:120px;" />
        <el-input v-model.number="customWorkHours" type="number" placeholder="工时" style="width:100px;" />
        <el-input v-model.number="customLeaves" type="number" placeholder="请假天数" style="width:120px;" />
        <el-input v-model.number="customLevel" type="number" placeholder="级别" style="width:100px;" />
        <el-input v-model.number="customExpected" type="number" placeholder="预期分数" style="width: 120px;" />
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
                <el-table-column label="输入(销售,工时,请假,级别)" width="240">
                  <template #default="scope">
                    <span class="input-mono">({{ scope.row.sales }}, {{ scope.row.work_hours }}, {{ scope.row.leaves }}, {{ scope.row.level }})</span>
                  </template>
                </el-table-column>
                <el-table-column prop="expected" label="预计分数" width="100" />
                <el-table-column prop="output_score" label="实际分数" width="100" />
                <el-table-column prop="description" label="用例说明" min-width="180" />
                <el-table-column label="结果" width="100" align="center">
                  <template #default="scope">
                     <span :class="scope.row.expected === 'N/A' ? '' : (scope.row.expected == scope.row.output_score ? 'table-result-pass' : 'table-result-fail')">
                       {{ scope.row.expected === 'N/A' ? 'N/A' : (scope.row.expected == scope.row.output_score ? '通过' : '失败') }}
                     </span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <!-- BVA test results table -->
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
                    <el-table-column label="输入(销售,工时,请假,级别)" width="240">
                      <template #default="scope">
                        <span class="input-mono">({{ scope.row.sales }}, {{ scope.row.work_hours }}, {{ scope.row.leaves }}, {{ scope.row.level }})</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="expected" label="预计分数" width="100" />
                    <el-table-column prop="output_score" label="实际分数" width="100" />
                    <el-table-column prop="description" label="用例说明" min-width="180" />
                    <el-table-column label="结果" width="100" align="center">
                      <template #default="scope">
                        <span :class="scope.row.expected == scope.row.output_score ? 'table-result-pass' : 'table-result-fail'">
                          {{ scope.row.expected == scope.row.output_score ? '通过' : '失败' }}
                        </span>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
            </div>

            <!-- Empty state -->
            <div v-else-if="!isLoading && !error" class="empty-state">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="empty-icon"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"></path><line x1="4" y1="22" x2="4" y2="15"></line></svg>
                <p>点击上方按钮开始测试</p>
            </div>
        </transition>
    </div>

  </div>
</template>

<style scoped>
/* Copied directly from TriangleTester.vue for consistency */
.tester-container {
    max-width: 1300px;
    margin: 0 auto;
}
.actions-bar {
  text-align: center;
  margin-bottom: 32px;
  display: flex;
  justify-content: center;
  gap: 16px;
}
.el-button {
    font-weight: 600;
    padding: 20px 30px;
    font-size: 1.1rem;
}
.error-alert {
  margin-bottom: 24px;
}
.summary-container {
    margin-bottom: 32px;
}
.statistic-card {
    background-color: var(--color-bg-card);
    border-radius: var(--border-radius);
    padding: 20px;
    box-shadow: var(--shadow);
    text-align: center;
}
.statistic-card.pass {
    border-left: 5px solid var(--color-success);
}
.statistic-card.fail {
    border-left: 5px solid var(--color-danger);
}
.results-table {
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}
.results-table :deep(.el-table__cell) {
    text-align: center;
}
.content-wrapper {
    min-height: 400px;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    width: 100%;
}
.loading-state, .empty-state {
    text-align: center;
    color: var(--color-text-light);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    margin-top: 100px;
}
.empty-icon { color: var(--color-primary); }
.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: var(--color-primary);
    animation: spin 1s ease infinite;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.custom-test-panel {
  padding: 28px;
  background: #fdfdff;
  border: 1px solid #e8eaf2;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(100,100,150,0.05);
  margin: 0 auto 32px auto;
  max-width: fit-content;
}
.custom-inputs {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}
.input-mono {
    font-family: 'JetBrains Mono', 'Fira Mono', 'Consolas', monospace;
}
.table-result-pass {
  color: var(--color-success);
  font-weight: bold;
}
.table-result-fail {
  color: var(--color-danger);
  font-weight: bold;
}
</style> 