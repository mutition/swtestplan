<script setup>
import { ref } from 'vue';
import { ElButton, ElTable, ElTableColumn, ElAlert, ElRow, ElCol, ElStatistic, ElIcon, ElInput, ElSelect, ElOption } from 'element-plus';
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue';

// --- reactive state ---
const testResults = ref([]);
const summary = ref(null);
const isLoading = ref(false);
const error = ref('');
const testType = ref('bva'); // bva, equivalence, or custom

// Equivalence class description visibility
const showEquiv = ref(true);
const toggleEquiv = () => { showEquiv.value = !showEquiv.value; };

// Custom test state
const customYear = ref('');
const customMonth = ref('');
const customDay = ref('');
const customExpected = ref('无效日期'); // Default to a common case
const customResults = ref([]);
const customTestIdCounter = ref(1);
const customLoading = ref(false);

// --- API call ---
const runTests = async (type) => {
  testType.value = type;
  error.value = '';
  if (type !== 'custom') {
    isLoading.value = true;
    testResults.value = [];
    summary.value = null;
    try {
      const response = await fetch(`http://127.0.0.1:5000/run-calendar-tests?type=${type}`);
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
    const response = await fetch('http://127.0.0.1:5000/run-calendar-custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        year: customYear.value || 0,
        month: customMonth.value || 0,
        day: customDay.value || 0
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '请求失败');
    
    const newResult = {
      id: `Custom-${customTestIdCounter.value++}`,
      year: data.year,
      month: data.month,
      day: data.day,
      expected: customExpected.value || 'N/A',
      output_type: data.output_type,
      description: '自定义测试用例',
    };
    customResults.value.unshift(newResult);

    customYear.value = '';
    customMonth.value = '';
    customDay.value = '';
    customExpected.value = '无效日期'; // Reset to default

  } catch (e) {
    error.value = '自定义测试失败: ' + e.message;
  } finally {
    customLoading.value = false;
  }
};

// --- Initial load ---
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
        :plain="testType !== 'equivalence'"
        @click="runTests('equivalence')"
        size="large"
      >
        等价类测试
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
          <li><strong>输入变量包括年y、月m、日d，下面依次对这三个输入变量做等价类划分：</strong></li>
          <li style="margin-top: 1em;"><strong>a. 按照 "year 年" 划分[1800, 2200]</strong>
              <ul style="padding-left: 20px; margin-top: 5px;">
                  <li>i. 世纪闰年：世纪年且整除400 <br/> Y1 = { y | y = 1000K && y = 400K, K为整数 }</li>
                  <li>ii. 普通闰年：普通年且整除4但不整除100 <br/> Y2 = { y | y = 4K && y != 100K, K为整数 }</li>
                  <li>iii. 非闰年 Y3</li>
                  <li>iv. 非法Y4：小于1800，或大于2200，或非整数</li>
              </ul>
          </li>
          <li style="margin-top: 1em;"><strong>b. 按照 "month 月" 划分[1, 12]</strong>
              <ul style="padding-left: 20px; margin-top: 5px;">
                  <li>i. 2月： M1 = {m = 2}</li>
                  <li>ii. 12月： M2 = {m = 12}</li>
                  <li>iii. 其余拥有31天的大月： M3 = {1, 3, 5, 7, 8, 10}</li>
                  <li>iv. 其余拥有30天的小月： M4 = {4, 6, 9, 11}</li>
                  <li>v. 非法M5：小于1，或大于12，或非整数</li>
              </ul>
          </li>
          <li style="margin-top: 1em;"><strong>c. 按照 "day 日" 划分[1, 31]</strong>
              <ul style="padding-left: 20px; margin-top: 5px;">
                  <li>i. D1 = {1 &lt;= d &lt;= 27}</li>
                  <li>ii. D2 = {d = 28}</li>
                  <li>iii. D3 = {d = 29}</li>
                  <li>iv. D4 = {d = 30}</li>
                  <li>v. D5 = {d = 31}</li>
                  <li>vi. 非法D6：小于1，或大于31，或非整数</li>
              </ul>
          </li>
          <li style="margin-top: 1em;"><strong>2. 综合可以得到12个等价类：</strong>
            <ul style="padding-left: 20px; margin-top: 5px;">
                <li>a. R1 = {&lt;Y, M, D&gt;: Y = Y1, Y2, M = M1, D = D1, D2} 闰年2月月中</li>
                <li>b. R2 = {&lt;Y, M, D&gt;: Y = Y1, Y2, M = M1, D = D3} 闰年2月月末</li>
                <li>c. R3 = {&lt;Y, M, D&gt;: Y = Y1, Y2, M = M1, D = D4, D5} 闰年2月非法</li>
                <li>d. R4 = {&lt;Y, M, D&gt;: Y = Y3, M = M1, D = D1} 普通年2月月中</li>
                <li>e. R5 = {&lt;Y, M, D&gt;: Y = Y3, M = M1, D = D2} 普通年2月月末</li>
                <li>f. R6 = {&lt;Y, M, D&gt;: Y = Y3, M = M1, D = D3, D4, D5} 普通年2月非法</li>
                <li>g. R7 = {&lt;Y, M, D&gt;: Y = Y1, Y2, Y3, M = M2, M3, D = D1, D2, D3, D4} 大月月中</li>
                <li>h. R8 = {&lt;Y, M, D&gt;: Y = Y1, Y2, Y3, M = M2, D = D5} 12月月末</li>
                <li>i. R9 = {&lt;Y, M, D&gt;: Y = Y1, Y2, Y3, M = M3, D = D5} 其余大月月末</li>
                <li>j. R10 = {&lt;Y, M, D&gt;: Y = Y1, Y2, Y3, M = M4, D = D1, D2, D3} 小月月中</li>
                <li>k. R11 = {&lt;Y, M, D&gt;: Y = Y1, Y2, Y3, M = M4, D = D4} 小月月末</li>
                <li>l. R12 = {&lt;Y, M, D&gt;: Y = Y1, Y2, Y3, M = M4, D = D5} 小月非法</li>
            </ul>
          </li>
        </ul>
      </transition>
    </div>

    <div v-if="testType === 'custom'" class="custom-test-panel">
      <div class="custom-inputs">
        <el-input v-model.number="customYear" type="number" placeholder="年" style="width:100px;" />
        <el-input v-model.number="customMonth" type="number" placeholder="月" style="width:100px;" />
        <el-input v-model.number="customDay" type="number" placeholder="日" style="width:100px;" />
        <el-input v-model="customExpected" placeholder="预期结果 (如 2024.3.1 或 无效日期)" style="width: 240px;" />
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
            
            <div v-else-if="testType === 'custom' && customResults.length > 0" class="results-table">
              <el-table :data="customResults" stripe style="width: 100%" border class="el-table">
                <el-table-column prop="id" label="编号" width="120" />
                <el-table-column label="输入(年,月,日)" width="180">
                  <template #default="scope"><span class="input-mono">({{ scope.row.year }}, {{ scope.row.month }}, {{ scope.row.day }})</span></template>
                </el-table-column>
                <el-table-column prop="expected" label="预计输出" width="140" />
                <el-table-column prop="output_type" label="实际输出" width="140" />
                <el-table-column prop="description" label="用例说明" min-width="180" />
                <el-table-column label="结果" width="120" align="center">
                  <template #default="scope">
                    <span :class="scope.row.expected === 'N/A' ? '' : (scope.row.expected === scope.row.output_type ? 'table-result-pass' : 'table-result-fail')">
                      {{ scope.row.expected === 'N/A' ? 'N/A' : (scope.row.expected === scope.row.output_type ? '通过' : '失败') }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
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
                    <el-table-column label="输入(年,月,日)" width="180">
                      <template #default="scope"><span class="input-mono">({{ scope.row.year }}, {{ scope.row.month }}, {{ scope.row.day }})</span></template>
                    </el-table-column>
                    <el-table-column prop="expected" label="预计输出" width="120" />
                    <el-table-column prop="output_type" label="实际输出" width="120" />
                    <el-table-column prop="description" label="用例说明" min-width="180" />
                    <el-table-column label="结果" width="100" align="center">
                      <template #default="scope">
                        <span :class="scope.row.expected === scope.row.output_type ? 'table-result-pass' : 'table-result-fail'">
                          {{ scope.row.expected === scope.row.output_type ? '通过' : '失败' }}
                        </span>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
            </div>

            <div v-else-if="!isLoading && !error" class="empty-state">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="empty-icon"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"></path><line x1="4" y1="22" x2="4" y2="15"></line></svg>
                <p>点击上方按钮开始测试</p>
            </div>
        </transition>
    </div>
  </div>
</template>

<style scoped>
/* Copied from TriangleTester.vue for consistency */
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
    background-color: var(--el-bg-color-overlay, #ffffff); /* Fallback for older ElementPlus */
    border-radius: 8px;
    padding: 20px;
    box-shadow: var(--el-box-shadow-light, 0px 0px 12px rgba(0, 0, 0, 0.12));
    text-align: center;
}
.statistic-card.pass {
    border-left: 5px solid #67c23a;
}
.statistic-card.fail {
    border-left: 5px solid #f56c6c;
}
.results-table {
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--el-box-shadow-light, 0 2px 12px 0 rgba(0,0,0,0.1));
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
    color: #909399;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    margin-top: 100px;
}
.empty-icon { color: #409eff; }
.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: #409eff;
    animation: spin 1s ease infinite;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.equiv-desc {
  background: #f8fafc;
  border-radius: 14px;
  box-shadow: 0 2px 12px 0 rgba(60,60,100,0.06);
  padding: 24px 32px 18px 32px;
  margin: 0 auto 32px auto;
  max-width: 900px;
  font-size: 17px;
}
.equiv-title {
  font-weight: 700;
  font-size: 19px;
  margin-bottom: 10px;
  color: #2563eb;
}
.equiv-list {
  margin: 0;
  padding-left: 18px;
}
.equiv-list li {
  margin-bottom: 6px;
  line-height: 1.7;
  font-family: 'Consolas', monospace;
  font-size: 16px;
  color: #374151;
}
.equiv-list b {
  color: #0ea5e9;
  font-weight: 700;
  font-size: 16.5px;
}

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
    font-family: 'Consolas', monospace;
}
.table-result-pass {
  color: #67c23a;
  font-weight: bold;
}
.table-result-fail {
  color: #f56c6c;
  font-weight: bold;
}
</style>