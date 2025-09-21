<template> 
    <div> 
      <h2>Lighting Controller Device Data Page</h2>
      <el-card class="mb-4">
        <div slot="header">Real-time Data</div>
        <div v-if="realTimeData && realTimeData.status!== null">
          <p><strong>Light Control Status:</strong> {{ realTimeData.status === 'on'? 'On' : 'Off' }}</p>
          <p><strong>Current Light Intensity:</strong> {{ realTimeData.intensity }} Lux</p>
          <p><strong>Time:</strong> {{ realTimeData.timestamp }}</p>
        </div>
        <div v-else-if="realTimeData === null">
          Loading...
        </div>
        <div v-else>
          No real-time data available.
        </div>
      </el-card>
      
      <el-card class="mt-4">
        <div slot="header">Light Intensity Variation Chart Over Time</div>
        <line-chart :chart-data="intensityChartData" :chart-options="intensityChartOptions" />
      </el-card>
      
      <el-card class="mt-4">
        <div slot="header">Bar Chart of Light Control Switch Status Proportion</div>
        <div style="width: 30%; margin: 0 auto;">
          <bar-chart :chart-data="switchStatusChartData" :chart-options="switchStatusChartOptions" />
        </div>
      </el-card>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import LineChart from '../components/LightingControllerLineChart.vue';
  import BarChart from '../components/LightingControllerBarChart.vue';
  
  export default {
    name: 'LightingControllerPage',
    components: {
      LineChart,
      BarChart
    },
    data() {
      return {
        deviceId: this.$route.params.deviceId || 'lightingController1',
        realTimeData: null,
        intensityChartData: {
          labels: [],
          datasets: [
            {
              label: 'Light Intensity (Lux)',
              data: [],
              borderColor: '#FFD700',
              fill: false,
              tension: 0.3
            }
          ]
        },
        intensityChartOptions: {
          responsive: true,
          animation: {
            duration: 500
          },
          scales: {
            x: {
              display: false
            },
            y: {
              title: {
                display: true,
                text: 'Light Intensity (Lux)'
              },
              suggestedMin: 0,
              suggestedMax: 1000
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        },
        switchStatusChartData: {
          labels: ['On', 'Off'],
          datasets: [
            {
              data: [0, 0],
              backgroundColor: ['#FFD700', '#FF6B6B']
            }
          ]
        },
        switchStatusChartOptions: {
          responsive: true,
          animation: {
            duration: 500
          },
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      };
    },
    created() {
      this.fetchAllData();
      this.interval = setInterval(this.fetchAllData, 5000);
    },
    beforeDestroy() {
      clearInterval(this.interval);
    },
    methods: {
      formatIsStarted(row) {
        return row.status === 'on'? 'On' : 'Off';
      },
      fetchAllData() { 
  axios.get('http://localhost:5050/api/history/light_control')
    .then(res => {
      const allData = res.data.history || [];
      const now = new Date();
      const fiveSecondsAgo = new Date(now.getTime() - 5000);
      const twoMinutesAgo = new Date(now.getTime() - 2 * 60 * 1000);

      // ✅ 获取最近 5 秒的实时数据
      const realTime = allData.find(item => {
        const ts = new Date(item.timestamp);
        return ts >= fiveSecondsAgo;
      });

      // ✅ 获取最近 2 分钟的数据用于画图
      const intensityChartDataPoints = allData.filter(item => {
        const ts = new Date(item.timestamp);
        return ts >= twoMinutesAgo;
      });

      // ⚠️ 设置实时数据到页面展示
      this.realTimeData = realTime || null;

      // ⚠️ 设置折线图数据
      this.intensityChartData = {
        labels: intensityChartDataPoints.map(() => ''),
        datasets: [
          {
            label: 'Light Intensity (Lux)',
            data: intensityChartDataPoints.map(item => item.intensity),
            borderColor: '#42A5F5', // 修改为蓝色
            fill: false,
            tension: 0.3
          }
        ]
      };

      // ✅ 统计过去 1 分钟的状态
      const allDataInOneMinute = allData.filter(item => {
        const ts = new Date(item.timestamp);
        return ts >= new Date(now.getTime() - 60 * 1000);
      });

      // ⚠️ 根据强度判断状态
      const tooBrightCount = allDataInOneMinute.filter(item => item.intensity >= 600).length;
      const tooDarkCount = allDataInOneMinute.filter(item => item.intensity <= 200).length;
      const offCount = allDataInOneMinute.length - tooBrightCount - tooDarkCount;

      // ⚠️ 更新柱状图数据
      this.switchStatusChartData = {
        labels: ['ON (Too Bright)', 'ON (Too Dark)', 'OFF'],
        datasets: [
          {
            label: 'Light Control Status',
            data: [tooBrightCount, tooDarkCount, offCount],
            backgroundColor: ['#FFA726', '#66BB6A', '#FF6B6B']
          }
        ]
      };
    })
    .catch(err => {
      console.error('Failed to fetch data:', err);
    });
}

    }
  };
  </script>
  
  <style scoped>
  .mb-4 {
    margin-bottom: 20px;
  }
  
  .mt-4 {
    margin-top: 20px;
  }
  </style>
  