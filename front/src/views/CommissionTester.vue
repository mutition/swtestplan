<script setup>
import { ref } from 'vue';
import { ElButton, ElTable, ElTableColumn, ElAlert, ElRow, ElCol, ElStatistic, ElInput } from 'element-plus';

const testResults = ref([]);
const summary = ref(null);
const isLoading = ref(false);
const error = ref('');
const testType = ref('bva'); // bva or custom

// Custom test state
const customHosts = ref('');
const customMonitors = ref('');
const customPeripherals = ref('');
const customExpectedSales = ref('');
const customExpectedCommission = ref('');
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
      const response = await fetch(`http://127.0.0.1:5000/run-commission-tests`);
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ message: '无法解析错误响应' }));
        throw new Error(`HTTP 错误！状态: ${response.status}. ${errData.message || ''}`);
      }
      const data = await response.json();
      testResults.value = data.results;
      summary.value = data.summary;
    } catch (e) {
      error.value = `获取测试数据失败: ${e.message}`;
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
    const response = await fetch('http://127.0.0.1:5000/run-commission-custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        hosts: customHosts.value || 0,
        monitors: customMonitors.value || 0,
        peripherals: customPeripherals.value || 0,
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || '请求失败');
    
    const isPassFailApplicable = customExpectedSales.value !== '' || customExpectedCommission.value !== '';
    let passed = false;
    if (isPassFailApplicable) {
        if (data.status === 'success') {
            const salesMatch = (customExpectedSales.value === '') || (data.sales == customExpectedSales.value);
            const commissionMatch = (customExpectedCommission.value === '') || (data.commission == customExpectedCommission.value);
            passed = salesMatch && commissionMatch;
        } else {
            passed = false; // Actual result is an error, but user expected success values
        }
    }

    const newResult = {
      id: `Custom-${customTestIdCounter.value++}`,
      hosts_sold: data.hosts_sold,
      monitors_sold: data.monitors_sold,
      peripherals_sold: data.peripherals_sold,
      expected_sales: customExpectedSales.value === '' ? 'N/A' : Number(customExpectedSales.value),
      expected_commission: customExpectedCommission.value === '' ? 'N/A' : Number(customExpectedCommission.value),
      output_status: data.status,
      output_sales: data.sales,
      output_commission: data.commission,
      output_message: data.message,
      description: '自定义测试用例',
      is_pass_fail_applicable: isPassFailApplicable,
      passed: passed,
    };
    customResults.value.unshift(newResult);

    // Clear inputs
    customHosts.value = '';
    customMonitors.value = '';
    customPeripherals.value = '';
    customExpectedSales.value = '';
    customExpectedCommission.value = '';

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
        <el-input v-model.number="customHosts" type="number" placeholder="主机销量" style="width:120px;" />
        <el-input v-model.number="customMonitors" type="number" placeholder="显示器销量" style="width:120px;" />
        <el-input v-model.number="customPeripherals" type="number" placeholder="外设销量" style="width:120px;" />
        <el-input v-model.number="customExpectedSales" type="number" placeholder="预期销售额" style="width:120px;" />
        <el-input v-model.number="customExpectedCommission" type="number" placeholder="预期佣金" style="width:120px;" />
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
                <el-table-column prop="id" label="编号" width="100" />
                <el-table-column label="输入(主,显,外)" width="180">
                  <template #default="scope">
                    <span class="input-mono">({{ scope.row.hosts_sold }}, {{ scope.row.monitors_sold }}, {{ scope.row.peripherals_sold }})</span>
                  </template>
                </el-table-column>
                <el-table-column label="预计输出" min-width="180">
                  <template #default="scope">
                      <div v-if="scope.row.expected_sales !== 'N/A' || scope.row.expected_commission !== 'N/A'">
                          <span>销售额: {{ scope.row.expected_sales }}</span><br/>
                          <span>佣金: {{ scope.row.expected_commission }}</span>
                      </div>
                      <div v-else>N/A</div>
                  </template>
                </el-table-column>
                <el-table-column label="实际输出" min-width="180">
                    <template #default="scope">
                        <div v-if="scope.row.output_status === 'success'">
                            <span>销售额: {{ scope.row.output_sales }}</span><br/>
                            <span>佣金: {{ scope.row.output_commission }}</span>
                        </div>
                        <div v-else>{{ scope.row.output_message }}</div>
                    </template>
                </el-table-column>
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
                    <el-table-column label="输入(主,显,外)" width="180">
                      <template #default="scope">
                        <span class="input-mono">({{ scope.row.hosts_sold }}, {{ scope.row.monitors_sold }}, {{ scope.row.peripherals_sold }})</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="预计输出" min-width="220">
                        <template #default="scope">
                            <div v-if="scope.row.expected_status === 'success'">
                                <span>销售额: {{ scope.row.expected_sales }}</span><br/>
                                <span>佣金: {{ scope.row.expected_commission }}</span>
                            </div>
                            <div v-else>非法输入</div>
                        </template>
                    </el-table-column>
                    <el-table-column label="实际输出" min-width="220">
                        <template #default="scope">
                            <div v-if="scope.row.output_status === 'success'">
                                <span>销售额: {{ scope.row.output_sales }}</span><br/>
                                <span>佣金: {{ scope.row.output_commission }}</span>
                            </div>
                            <div v-else>{{ scope.row.output_message }}</div>
                        </template>
                    </el-table-column>
                    <el-table-column prop="description" label="用例说明" min-width="180" />
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
              <p>点击上方按钮开始测试</p>
            </div>
        </transition>
    </div>

  </div>
</template>

<style scoped>
/* Copied directly from TriangleTester.vue for consistency */
.tester-container { max-width: 1300px; margin: 0 auto; }
.actions-bar {
  text-align: center;
  margin-bottom: 32px;
  display: flex;
  justify-content: center;
  gap: 16px;
}
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
.input-mono { font-family: 'JetBrains Mono', 'Fira Mono', 'Consolas', monospace; }
.table-result-pass { color: var(--color-success); font-weight: bold; }
.table-result-fail { color: var(--color-danger); font-weight: bold; }
</style> 