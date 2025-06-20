<script setup>
import { ref } from 'vue';
import { ElButton, ElTable, ElTableColumn, ElAlert, ElCard, ElTag, ElDescriptions, ElDescriptionsItem } from 'element-plus';

const isLoading = ref(false);
const error = ref('');
const testInfo = ref(null);
const testResults = ref([]);

const runTests = async () => {
  isLoading.value = true;
  error.value = '';
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
</script>

<template>
  <div class="tester-container">
    <div class="actions-bar">
      <el-button type="primary" :loading="isLoading" @click="runTests" size="large">
        集成测试
      </el-button>
    </div>
    <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" :closable="false" />
    <div class="content-wrapper">
      <transition name="fade" mode="out-in">
        <div v-if="isLoading" class="loading-state">
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
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style> 