<script setup>
import { ref, computed } from 'vue';
import { ElButton, ElTable, ElTableColumn, ElAlert, ElRow, ElCol, ElStatistic, ElIcon, ElInput, ElSelect, ElOption } from 'element-plus';
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue';

const testResults = ref([]);
const summary = ref(null);
const isLoading = ref(false);
const error = ref('');
const testType = ref('bva'); // bva, equivalence, 或 custom

// 折叠依据
const showEquiv = ref(true);
const toggleEquiv = () => { showEquiv.value = !showEquiv.value; };

// 自定义测试的状态
const customA = ref('');
const customB = ref('');
const customC = ref('');
const customExpected = ref('非三角形'); // 默认预期
const customResults = ref([]); // 存储所有自定义测试结果
const customTestIdCounter = ref(1);
const customLoading = ref(false);
const expectedOptions = ['等边三角形', '等腰三角形', '一般三角形', '非三角形'];

const runTests = async (type) => {
  // 切换模式时重置状态
  testType.value = type;
  error.value = '';
  if (type !== 'custom') {
    isLoading.value = true;
    testResults.value = [];
    summary.value = null;
    try {
      const response = await fetch(`http://127.0.0.1:5000/run-triangle-tests?type=${type}`);
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
    // 切换到自定义模式时，清空旧的批量测试结果
    summary.value = null;
    testResults.value = [];
  }
};

const runCustomTest = async () => {
  customLoading.value = true;
  error.value = '';
  try {
    const response = await fetch('http://127.0.0.1:5000/run-triangle-custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ a: customA.value || 0, b: customB.value || 0, c: customC.value || 0 })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '请求失败');
    
    // 构建与另外两种模式完全一致的结果对象
    const newResult = {
      id: `Custom-${customTestIdCounter.value++}`,
      a: data.a,
      b: data.b,
      c: data.c,
      expected: customExpected.value,
      output_type: data.output_type,
      description: '自定义测试用例',
    };
    customResults.value.unshift(newResult); // 添加到列表顶部

    // 清空输入框以便下次输入
    customA.value = '';
    customB.value = '';
    customC.value = '';

  } catch (e) {
    error.value = '自定义测试失败: ' + e.message;
  } finally {
    customLoading.value = false;
  }
};

// 自动加载一次默认用例
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
          <li><b>D1</b> = {'&lt;a,b,c&gt;:a=b=c'}</li>
          <li><b>D21</b> = {'&lt;a,b,c&gt;:a=b,a≠c,a+b&gt;c'}</li>
          <li><b>D22</b> = {'&lt;a,b,c&gt;:a=b,a≠c,a+b≤c'}</li>
          <li><b>D31</b> = {'&lt;a,b,c&gt;:a=c,a≠b,a+c&gt;b'}</li>
          <li><b>D32</b> = {'&lt;a,b,c&gt;:a=c,a≠b,a+c≤b'}</li>
          <li><b>D41</b> = {'&lt;a,b,c&gt;:b=c,a≠b,b+c&gt;a'}</li>
          <li><b>D42</b> = {'&lt;a,b,c&gt;:b=c,a≠b,b+c≤a'}</li>
          <li><b>D5</b> = {'&lt;a,b,c&gt;:a≠b,a≠c,b≠c,且任意两边之和大于第三边'}</li>
        </ul>
      </transition>
    </div>

    <div v-if="testType === 'custom'" class="custom-test-panel">
      <div class="custom-inputs">
        <el-input v-model.number="customA" type="number" placeholder="边 a" style="width:100px;" />
        <el-input v-model.number="customB" type="number" placeholder="边 b" style="width:100px;" />
        <el-input v-model.number="customC" type="number" placeholder="边 c" style="width:100px;" />
        <el-select v-model="customExpected" placeholder="预期结果" style="width: 160px;">
          <el-option
            v-for="item in expectedOptions"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
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
            
            <!-- 自定义测试结果展示区 -->
            <div v-else-if="testType === 'custom' && customResults.length > 0" class="results-table">
              <el-table :data="customResults" stripe style="width: 100%" border class="el-table">
                <el-table-column prop="id" label="编号" width="120" />
                <el-table-column label="输入(a, b, c)" width="180">
                  <template #default="scope">
                    <span class="input-mono">({{ scope.row.a }}, {{ scope.row.b }}, {{ scope.row.c }})</span>
                  </template>
                </el-table-column>
                <el-table-column prop="expected" label="预计输出" width="140" />
                <el-table-column prop="output_type" label="实际输出" width="140" />
                <el-table-column prop="description" label="用例说明" min-width="180" />
                <el-table-column label="结果" width="120" align="center">
                  <template #default="scope">
                    <span :class="scope.row.expected === scope.row.output_type ? 'table-result-pass' : 'table-result-fail'">
                      {{ scope.row.expected === scope.row.output_type ? '通过' : '失败' }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div v-else-if="summary" class="summary-and-results">
                <div class="summary-container">
                     <el-row :gutter="20">
                        <el-col :span="8">
                            <div class="statistic-card">
                                <el-statistic title="总用例数" :value="summary.totalCount" />
                            </div>
                        </el-col>
                        <el-col :span="8">
                            <div class="statistic-card pass">
                                <el-statistic title="通过用例" :value="summary.passCount" />
                            </div>
                        </el-col>
                         <el-col :span="8">
                            <div class="statistic-card fail">
                                <el-statistic title="失败用例" :value="summary.totalCount - summary.passCount" />
                            </div>
                        </el-col>
                    </el-row>
                </div>

                <div class="results-table">
                  <el-table :data="testResults" stripe style="width: 100%" border class="el-table">
                    <el-table-column prop="id" label="编号" width="100" />
                    <el-table-column label="输入(a, b, c)" width="180">
                      <template #default="scope">
                        <span class="input-mono">({{ scope.row.a }}, {{ scope.row.b }}, {{ scope.row.c }})</span>
                      </template>
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
  font-family: 'JetBrains Mono', 'Fira Mono', 'Consolas', monospace;
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
</style> 