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
            <el-image 
              :src="'http://localhost:8000/api/image-proxy?path=' + photo.path" 
              lazy 
              fit="cover"
              class="bird-thumb"
            />
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
const scanPath = ref('D:/Photos/Birds')
const isScanning = ref(false)
const scanProgress = ref(0)
const treeData = ref([])
const currentPhotos = ref([])
const selectedPhoto = ref(null)
const filterText = ref('')
const treeRef = ref()

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
    await axios.post('http://localhost:8000/api/scan', { paths: [scanPath.value] })
    pollStatus()
  } catch (err) {
    ElMessage.error('启动扫描失败')
    isScanning.value = false
  }
}

// 2. 轮询扫描进度
const pollStatus = () => {
  const timer = setInterval(async () => {
    const res = await axios.get('http://localhost:8000/api/status')
    if (res.data.status === 'completed') {
      clearInterval(timer)
      isScanning.value = false
      loadTree()
    }
  }, 1000)
}

// 3. 加载树结构
const loadTree = async () => {
  const res = await axios.get('http://localhost:8000/api/tree')
  treeData.value = [res.data]
}

// 4. 点击节点处理
const handleNodeClick = (node) => {
  if (node.rank === 'Species') {
    currentPhotos.value = node.photos || []
  }
}

// 5. 定位文件
const locateFile = () => {
  // 这里可以调用后端 API 让后端执行 os.startfile 或 shell 逻辑
  axios.get(`http://localhost:8000/api/locate?path=${selectedPhoto.value.path}`)
}

const selectPhoto = (photo) => { selectedPhoto.value = photo }

// 树过滤逻辑
watch(filterText, (val) => {
  treeRef.value?.filter(val)
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