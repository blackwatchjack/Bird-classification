<template>
  <el-container class="layout-container">
    <el-header>
      <div class="header-content">
        <span>鸟类照片虚拟索引系统 (IOC 15.1)</span>
        <div class="scan-controls">
          <el-input v-model="scanPath" placeholder="输入文件夹路径" style="width: 300px" />
          <el-button type="primary" :loading="isScanning" @click="startScan">开始扫描</el-button>
          <el-progress v-if="isScanning" :percentage="scanProgress" :format="progressFormat" />
        </div>
      </div>
    </el-header>

    <el-container>
      <el-aside width="350px">
        <el-input v-model="filterText" placeholder="搜索物种..." class="filter-input" />
        <el-tree-v2
          ref="treeRef"
          :data="treeData"
          :props="treeProps"
          :height="800"
          :filter-method="filterNode"
          @node-click="handleNodeClick"
        />
      </el-aside>

      <el-main>
        <el-empty v-if="currentPhotos.length === 0" description="点击左侧物种查看照片" />
        <div class="photo-grid">
          <div v-for="photo in currentPhotos" :key="photo.path" class="photo-card" @click="selectPhoto(photo)">
            <!-- <el-image 
              :src="'/api/image-proxy?path=' + photo.path" 
              lazy 
              fit="cover"
              class="bird-thumb"
            /> -->
            <el-image 
              :src="`/api/thumbnail?path=${encodeURIComponent(photo.path)}&size=200`" 
              lazy 
              fit="cover"
              class="bird-thumb"
            >
              <template #placeholder>
                <div class="image-slot">加载中...</div>
              </template>
              <template #error>
                <el-icon><Picture /></el-icon>
              </template>
            </el-image>
            <div class="photo-name">{{ photo.name }}</div>
          </div>
        </div>
      </el-main>

      <el-aside v-if="selectedPhoto" width="280px" class="detail-panel">
        <el-descriptions title="照片详情" :column="1" border>
          <el-descriptions-item label="文件名">{{ selectedPhoto.name }}</el-descriptions-item>
          <el-descriptions-item label="物理路径">
            <span class="path-text">{{ selectedPhoto.path }}</span>
          </el-descriptions-item>
        </el-descriptions>
        <el-button type="success" class="locate-btn" @click="locateFile">在资源管理器中定位</el-button>
      </el-aside>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// --- 响应式数据 ---
const scanPath = ref('Ur bird photos folder path')
const isScanning = ref(false)
const scanProgress = ref(0)
const treeData = ref([])
const currentPhotos = ref([])
const selectedPhoto = ref(null)
const filterText = ref('')
const treeRef = ref()
const pollTimer = ref(null)

const treeProps = {
  value: 'id',
  label: 'label',
  children: 'children',
}

// --- 逻辑方法 ---

// 1. 发起扫描请求
const startScan = async () => {
  isScanning.value = true
  try {
    await axios.post('/api/scan', { paths: [scanPath.value] }, { timeout: 15000 })
    pollStatus()
  } catch (err) {
    ElMessage.error('启动扫描失败')
    isScanning.value = false
  }
}

// 2. 轮询扫描进度
const pollStatus = () => {
  // 清除可能存在的旧定时器
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
  }
  
  const startTime = Date.now()
  const MAX_POLL_TIME = 300000 // 最大轮询时间：5分钟
  
  pollTimer.value = setInterval(async () => {
    try {
      // 检查是否超过最大轮询时间
      if (Date.now() - startTime > MAX_POLL_TIME) {
        clearInterval(pollTimer.value)
        pollTimer.value = null
        isScanning.value = false
        ElMessage.error('扫描超时')
        return
      }
      
      const res = await axios.get('/api/status')
      if (res.data.status === 'completed') {
        scanProgress.value = 100
        clearInterval(pollTimer.value)
        pollTimer.value = null
        isScanning.value = false
        loadTree()
        ElMessage.success(`扫描完成：共扫描${res.data.scanned}个文件，匹配${res.data.matched}个物种照片`)
      }
    } catch (err) {
      clearInterval(pollTimer.value)
      pollTimer.value = null
      isScanning.value = false
      ElMessage.error('轮询扫描进度失败')
    }
  }, 1000)
}

// 3. 加载树结构
const loadTree = async () => {
  const res = await axios.get('/api/tree')
  treeData.value = [res.data]
}

// 4. 点击节点处理
const handleNodeClick = (node) => {
  if (node.rank === 'Species') {
    currentPhotos.value = node.photos || []
  }
}

// 5. 定位文件
// 在 <script setup> 中添加
const locateFile = async () => {
  if (!selectedPhoto.value) return;
  
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/locate', {
      params: { path: selectedPhoto.value.path }
    });
    ElMessage.success('已打开资源管理器');
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '定位失败');
  }
};

const selectPhoto = (photo) => { selectedPhoto.value = photo }

// 树过滤逻辑
watch(filterText, (val) => {
  treeRef.value?.filter(val)
})

// 监听扫描状态变化，停止轮询
watch(isScanning, (newVal) => {
  if (!newVal && pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
})

const filterNode = (value, data) => {
  if (!value) return true
  return data.label.includes(value)
}
</script>

<style scoped>
/* 样式建议：使用 Flex 布局确保高度铺满屏幕 */
.layout-container { height: 100vh; }
.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}
.photo-card { cursor: pointer; border: 1px solid #eee; padding: 5px; }
.bird-thumb { width: 150px; height: 150px; border-radius: 4px; }
.path-text { font-size: 12px; color: #666; word-break: break-all; }
.locate-btn { margin-top: 20px; width: 100%; }
</style>