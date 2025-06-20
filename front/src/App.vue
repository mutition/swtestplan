<script setup>
import { ref } from 'vue';
import TriangleTester from './views/TriangleTester.vue';
import CalendarTester from './views/CalendarTester.vue';
import EvaluationTester from './views/EvaluationTester.vue';
import CommissionTester from './views/CommissionTester.vue';
import TelecomTester from './views/TelecomTester.vue';
import ForumTester from './views/ForumTester.vue';

const currentTest = ref('triangle');
</script>

<template>
  <div class="layout-root">
    <aside class="sidebar">
      <div class="logo-bar">
        <span class="logo-icon">🧪</span>
        <span class="logo-text">自动化测试平台</span>
      </div>
      <nav class="nav-list">
        <div
          class="nav-item"
          :class="{ active: currentTest === 'triangle' }"
          @click="currentTest = 'triangle'"
        >
          <span class="nav-icon">▲</span>
          <span>三角形测试</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: currentTest === 'calendar' }"
          @click="currentTest = 'calendar'"
        >
          <span class="nav-icon">📅</span>
          <span>万年历测试</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: currentTest === 'evaluation' }"
          @click="currentTest = 'evaluation'"
        >
          <span class="nav-icon">📈</span>
          <span>销售考评测试</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: currentTest === 'commission' }"
          @click="currentTest = 'commission'"
        >
          <span class="nav-icon">💰</span>
          <span>佣金计算测试</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: currentTest === 'telecom' }"
          @click="currentTest = 'telecom'"
        >
          <span class="nav-icon">📞</span>
          <span>电信收费测试</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: currentTest === 'forum' }"
          @click="currentTest = 'forum'"
        >
          <span class="nav-icon">💬</span>
          <span>论坛测试</span>
        </div>
        <!-- 未来可扩展：其他测试项目 -->
      </nav>
    </aside>
    <main class="main-content">
      <TriangleTester v-if="currentTest === 'triangle'" />
      <CalendarTester v-if="currentTest === 'calendar'" />
      <EvaluationTester v-if="currentTest === 'evaluation'" />
      <CommissionTester v-if="currentTest === 'commission'" />
      <TelecomTester v-if="currentTest === 'telecom'" />
      <ForumTester v-if="currentTest === 'forum'" />
  </main>
  </div>
</template>

<style scoped>
.layout-root {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(120deg, #f8fafc 0%, #e0e7ef 100%);
  font-family: 'Inter', 'HarmonyOS Sans', 'Segoe UI', Arial, sans-serif;
}

.sidebar {
  width: 300px;
  background: #fff;
  border-right: 1.5px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  box-shadow: 2px 0 16px 0 rgba(60,60,100,0.04);
}

.logo-bar {
  height: 60px;
    display: flex;
  align-items: center;
  padding-left: 28px;
  background: #f5f7fa;
  border-bottom: 1.5px solid #e5e7eb;
  font-family: 'Inter', 'HarmonyOS Sans', Arial, sans-serif;
  }
.logo-icon {
  font-size: 2.1rem;
  margin-right: 10px;
  filter: drop-shadow(0 2px 2px #e0e7ef);
}
.logo-text {
  font-size: 1.45rem;
  font-weight: 800;
  color: #3b3b4f;
  letter-spacing: 1.5px;
  text-shadow: 0 1px 0 #fff;
  }

.nav-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 32px 0 0 0;
  gap: 10px;
}

.nav-item {
    display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 28px 14px 36px;
  font-size: 1.18rem;
  color: #7b8190;
  cursor: pointer;
  border-radius: 12px 0 0 12px;
  margin-right: 18px;
  transition: background 0.18s, color 0.18s, box-shadow 0.18s;
  user-select: none;
  font-weight: 500;
}
.nav-item:hover {
  background: #f0f4ff;
  color: #3b3b4f;
  box-shadow: 2px 2px 8px 0 rgba(60,60,100,0.06);
}
.nav-item.active {
  color: #fff;
  background: linear-gradient(90deg, #6366f1 60%, #60a5fa 100%);
  box-shadow: 2px 4px 16px 0 rgba(99,102,241,0.08);
  font-weight: 700;
}
.nav-icon {
  font-size: 1.2em;
  margin-right: 2px;
}

.main-content {
  flex: 1;
  padding: 36px 36px 36px 36px;
  min-width: 0;
  background: none;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}
</style>