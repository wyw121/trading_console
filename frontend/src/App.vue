<template>
          <el-config-provider :locale="locale">
                    <div id="app">
                              <router-view />
                    </div>
          </el-config-provider>
</template>

<script setup>
import { ref } from 'vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const locale = ref(zhCn)
</script>

<style>
* {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
}

body {
          font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
          background-color: #f5f7fa;
}

#app {
          height: 100vh;
}

.main-container {
          padding: 20px;
}

.page-header {
          margin-bottom: 20px;
}

.page-title {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 8px;
}

.page-description {
          color: #606266;
          font-size: 14px;
}

.card-container {
          margin-bottom: 20px;
}

.flex-between {
          display: flex;
          justify-content: space-between;
          align-items: center;
}

.text-success {
          color: #67c23a;
}

.text-warning {
          color: #e6a23c;
}

.text-danger {
          color: #f56c6c;
}

.text-info {
          color: #909399;
}
</style>
