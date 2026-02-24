<template>
  <div class="h-[300px]" id="traffic-chart-wrapper">
    <div v-if="loading" id="chart-loading" class="flex h-full items-center justify-center">
      <svg class="h-8 w-8 animate-spin text-indigo-600" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
    </div>
    <div v-else-if="error" id="chart-error" class="flex h-full items-center justify-center text-red-500">
      {{ error }}
    </div>
    <div v-else id="chart-container" class="h-full w-full">
        <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import axios from 'axios'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps({
  websiteId: {
    type: Number,
    required: true
  }
})

const loading = ref(true)
const error = ref(null)
const chartData = ref({
  labels: [],
  datasets: []
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    },
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        drawBorder: false,
        color: 'rgba(0, 0, 0, 0.1)'
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}

const fetchData = async () => {
  loading.value = true
  error.value = null
  try {
    const { data } = await axios.get(`/api/v1/websites/${props.websiteId}/analytics`)

    chartData.value = {
      labels: data.labels,
      datasets: [
        {
          label: 'Requests',
          data: data.requests,
          borderColor: '#4f46e5', // indigo-600
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Unique Visitors',
          data: data.unique_visitors,
          borderColor: '#10b981', // emerald-500
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    }
  } catch (e) {
    error.value = "Failed to load analytics data"
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (props.websiteId) {
    fetchData()
  }
})

watch(() => props.websiteId, (newId) => {
  if (newId) {
    fetchData()
  }
})
</script>
