<script setup>
import { ref } from 'vue';
import { ElButton, ElTable, ElTableColumn, ElAlert, ElCard, ElTag, ElDescriptions, ElDescriptionsItem } from 'element-plus';

const isLoading = ref(false);
const error = ref('');
const testInfo = ref(null);
const testResults = ref([]);

const isSystemLoading = ref(false);
const systemError = ref('');
const systemLogContent = ref('');
const systemCases = ref([]);

const isUnitLoading = ref(false);
const unitError = ref('');
const unitTestResult = ref(null);

const runTests = async () => {
  isLoading.value = true;
  error.value = '';
  systemLogContent.value = '';
  systemError.value = '';
  unitError.value = '';
  unitTestResult.value = null;
  try {
    const response = await fetch('http://127.0.0.1:5000/api/run-forum-tests');
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || '请求失败');
    // 解析 test_info
    testInfo.value = data.test_info || null;
    // 解析 test_results
    if (data.test_results && typeof data.test_results === 'object') {
      testResults.value = Object.entries(data.test_results).map(([key, value], idx) => {
        return {
          id: idx + 1,
          name: key,
          description: value.result.api_info?.description || '',
          method: value.result.api_info?.method || '',
          path: value.result.api_info?.path || '',
          input: value.input_data,
          http_code: value.result.http_code,
          response_time: value.result.response_time,
          status: value.result.status,
          status_message: value.result.status_message,
          response_body: value.result.response_body,
        };
      });
    } else {
      testResults.value = [];
    }
  } catch (e) {
    error.value = '获取测试数据失败: ' + e.message;
  } finally {
    isLoading.value = false;
  }
};

const runSystemTests = async () => {
  isSystemLoading.value = true;
  systemError.value = '';
  testInfo.value = null;
  testResults.value = [];
  error.value = '';
  unitError.value = '';
  unitTestResult.value = null;
  try {
    const response = await fetch('http://127.0.0.1:5000/api/run-system-tests');
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || '运行系统测试失败');
    }
    systemLogContent.value = data.log;
    systemCases.value = Array.isArray(data.cases) ? data.cases : [];
  } catch (e) {
    systemError.value = '获取系统测试数据失败: ' + e.message;
    systemCases.value = [];
  } finally {
    isSystemLoading.value = false;
  }
};

const runUnitTests = async () => {
  isUnitLoading.value = true;
  unitError.value = '';
  // Clear other states
  error.value = '';
  testInfo.value = null;
  testResults.value = [];
  systemError.value = '';
  systemLogContent.value = '';
  systemCases.value = [];

  try {
    const response = await fetch('http://127.0.0.1:5000/api/run-unit-tests');
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || '运行单元测试失败');
    }
    unitTestResult.value = data;
  } catch (e) {
    unitError.value = '获取单元测试数据失败: ' + e.message;
  } finally {
    isUnitLoading.value = false;
  }
};
</script>

<template>
  <div class="tester-container">
    <div class="actions-bar">
      <el-button type="primary" :loading="isLoading" @click="runTests" size="large">
        集成测试
      </el-button>
      <el-button type="warning" :loading="isUnitLoading" @click="runUnitTests" size="large">
        单元测试
      </el-button>
      <el-button type="success" :loading="isSystemLoading" @click="runSystemTests" size="large">
        系统测试
      </el-button>
    </div>
    <el-alert v-if="error || systemError || unitError" :title="error || systemError || unitError" type="error" show-icon class="error-alert" :closable="false" />
    <div class="content-wrapper">
      <transition name="fade" mode="out-in">
        <div v-if="isLoading || isSystemLoading || isUnitLoading" class="loading-state">
          <div class="spinner"></div>
          <p>正在从服务器获取测试结果...</p>
        </div>
        <div v-else-if="testInfo" class="summary-and-results">
          <el-card class="summary-card" shadow="hover">
            <el-descriptions title="测试统计信息" :column="3" border>
              <el-descriptions-item label="测试时间">{{ testInfo.test_time }}</el-descriptions-item>
              <el-descriptions-item label="基准URL">{{ testInfo.base_url }}</el-descriptions-item>
              <el-descriptions-item label="总用例数">{{ testInfo.total_tests }}</el-descriptions-item>
              <el-descriptions-item label="通过用例">{{ testInfo.passed_tests }}</el-descriptions-item>
              <el-descriptions-item label="失败用例">{{ testInfo.failed_tests }}</el-descriptions-item>
              <el-descriptions-item label="通过率">{{ testInfo.success_rate }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
          <div class="results-table">
            <el-table :data="testResults" stripe style="width: 100%" border class="el-table">
              <el-table-column prop="id" label="编号" width="60" />
              <el-table-column prop="description" label="接口描述" min-width="120" />
              <el-table-column prop="method" label="方法" width="80">
                <template #default="scope">
                  <el-tag :type="scope.row.method==='POST'?'warning':'success'" disable-transitions>{{ scope.row.method }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="path" label="路径" min-width="180" />
              <el-table-column label="输入参数" min-width="180">
                <template #default="scope">
                  <pre style="font-size:13px;white-space:pre-wrap;word-break:break-all;max-width:320px;">{{ JSON.stringify(scope.row.input, null, 2) }}</pre>
                </template>
              </el-table-column>
              <el-table-column prop="http_code" label="HTTP状态" width="100" />
              <el-table-column prop="response_time" label="响应时间(s)" width="120" />
              <el-table-column prop="status" label="结果" width="80">
                <template #default="scope">
                  <el-tag :type="scope.row.status==='passed'?'success':'danger'" disable-transitions>{{ scope.row.status==='passed'?'通过':'失败' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status_message" label="状态信息" min-width="120" />
              <el-table-column label="响应内容" min-width="200">
                <template #default="scope">
                  <pre style="font-size:13px;white-space:pre-wrap;word-break:break-all;max-width:320px;">{{ scope.row.response_body }}</pre>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        <el-card v-else-if="systemLogContent || systemCases.length" class="log-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>系统测试结果</span>
            </div>
          </template>
          <div v-if="systemCases.length" class="sys-summary-bar">
            <el-tag type="info" effect="plain">总用例数：{{ systemCases.length }}</el-tag>
            <el-tag type="success" effect="plain">通过：{{ systemCases.filter(i=>i.result==='PASSED').length }}</el-tag>
            <el-tag type="danger" effect="plain">失败：{{ systemCases.filter(i=>i.result==='FAILED').length }}</el-tag>
            <el-tag type="warning" effect="plain">其他：{{ systemCases.filter(i=>i.result!=='PASSED'&&i.result!=='FAILED').length }}</el-tag>
            <el-tag type="primary" effect="plain">通过率：{{ ((systemCases.filter(i=>i.result==='PASSED').length / systemCases.length) * 100).toFixed(1) }}%</el-tag>
          </div>
          <el-table v-if="systemCases.length" :data="systemCases" stripe style="width: 100%;margin:18px 0 24px 0;" border>
            <el-table-column prop="file" label="文件名" min-width="180">
              <template #default="scope">
                <span style="word-break:break-all;">{{ scope.row.file }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="case" label="用例名" min-width="180">
              <template #default="scope">
                <span style="word-break:break-all;">{{ scope.row.case }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="result" label="结果" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.result==='PASSED'?'success':(scope.row.result==='FAILED'?'danger':'info')" disable-transitions>
                  {{ scope.row.result==='PASSED'?'通过':(scope.row.result==='FAILED'?'失败':scope.row.result) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div class="log-title-bar">
            <el-tag type="info" effect="dark">原始日志</el-tag>
          </div>
          <pre class="log-output">{{ systemLogContent }}</pre>
        </el-card>
        <el-card v-else-if="unitTestResult" class="log-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>单元测试结果</span>
            </div>
          </template>
          <pre class="log-output">{{ JSON.stringify(unitTestResult, null, 2) }}</pre>
        </el-card>
        <div v-else-if="!isLoading && !isSystemLoading && !isUnitLoading && !error && !systemError && !unitError" class="empty-state">
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
.summary-card {
  margin-bottom: 32px;
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
.sys-summary-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}
.log-title-bar {
  margin: 12px 0 4px 0;
}
.log-card {
  width: 100%;
}
.log-output {
  background-color: #f8f9fa;
  color: #212529;
  padding: 1.2rem;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  font-size: 13px;
  line-height: 1.5;
  border: 1px solid #e9ecef;
  margin-bottom: 0;
  max-height: 400px;
  overflow: auto;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style> 
