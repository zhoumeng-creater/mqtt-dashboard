<template>
  <div class="device-control-container">
    <!-- 页面顶部标题 -->
    <h2 style="text-align: center; margin-top: 20px; margin-bottom: 20px; font-weight: bold;">
      Device Control
    </h2>

    <!-- 手动模式切换 -->
    <el-switch
      v-model="manualMode"
      active-text="Manual Mode"
      inactive-text="Auto Mode"
      @change="toggleManualMode"
    />

    <!-- 第一行：Lighting 和 Water Heater -->
    <el-row :gutter="20" class="device-grid">
      <!-- 左上 - 灯光控制 -->
      <el-col :span="12">
        <el-card shadow="hover" style="min-height: 320px;">
          <h3>Lighting Control</h3>
          <p><strong>Status:</strong> {{ lightingStatus }}</p>
          <el-button type="success" @click="controlDevice('lighting', 'brighter')" :disabled="!manualMode">Brighter</el-button>
          <el-button type="warning" @click="controlDevice('lighting', 'dimmer')" :disabled="!manualMode">Dimmer</el-button>
          <el-button type="danger" @click="controlDevice('lighting', 'off')" :disabled="!manualMode">Turn Off</el-button>
          <el-button type="primary" @click="viewDeviceData('lighting')" style="margin-left: 10px">View Data</el-button>

          <div v-if="showLightingData" class="device-data-box">
            <h4>Latest Data:</h4>
            <pre>{{ JSON.stringify(lightingData, null, 2) }}</pre>
            <el-button type="primary" size="mini" @click="refreshDeviceData('lighting')">Refresh</el-button>
            <el-button type="danger" size="mini" @click="closeDeviceData('lighting')" style="margin-left: 5px;">Close</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右上 - 热水器 -->
      <el-col :span="12">
        <el-card shadow="hover" style="min-height: 320px;">
          <h3>Water Heater</h3>
          <p><strong>Status:</strong> {{ waterHeaterStatus }}</p>
          <el-button type="primary" @click="toggleHeater" :disabled="!manualMode">{{ heaterButtonText }}</el-button>
          <el-button type="primary" @click="viewDeviceData('water_heater')" style="margin-left: 10px">View Data</el-button>

          <div v-if="showWaterHeaterData" class="device-data-box">
            <h4>Latest Data:</h4>
            <pre>{{ JSON.stringify(waterHeaterData, null, 2) }}</pre>
            <el-button type="primary" size="mini" @click="refreshDeviceData('water_heater')">Refresh</el-button>
            <el-button type="danger" size="mini" @click="closeDeviceData('water_heater')" style="margin-left: 5px;">Close</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：Camera 和 Air Conditioner -->
    <el-row :gutter="20" class="device-grid">
      <!-- 左下 - 摄像头 -->
      <el-col :span="12">
        <el-card shadow="hover" style="min-height: 320px;">
          <h3>Surveillance Camera</h3>
          <p><strong>Status:</strong> {{ manualMode ? cameraStatus : "N/A" }}</p>

          <el-button type="primary" @click="enableCamera" :disabled="!manualMode || cameraStatus === 'on'">Enable Camera</el-button>
          <el-button type="danger" @click="disableCamera" :disabled="!manualMode || cameraStatus === 'off'" style="margin-left: 5px">Stop Camera</el-button>
          <el-button type="primary" @click="viewDeviceData('camera')" style="margin-left: 5px">View Data</el-button>

          <div v-if="cameraStatus === 'on'" class="camera-video-box">
            <video ref="cameraVideo" autoplay muted playsinline style="width: 100%; border-radius: 6px; margin-top: 10px;"></video>
          </div>

          <div v-if="showCameraData" class="device-data-box">
            <h4>Latest Data:</h4>
            <pre>{{ JSON.stringify(cameraData, null, 2) }}</pre>
            <el-button type="primary" size="mini" @click="refreshDeviceData('camera')">Refresh</el-button>
            <el-button type="danger" size="mini" @click="closeDeviceData('camera')" style="margin-left: 5px;">Close</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右下 - 空调 -->
      <el-col :span="12">
        <el-card shadow="hover" style="min-height: 320px;">
          <h3>Air Conditioner</h3>
          <p><strong>Cooling:</strong> {{ manualMode ? coolingStatus : "N/A" }}</p>
          <p><strong>Dehumidifying:</strong> {{ manualMode ? dehumidifyingStatus : "N/A" }}</p>

          <div style="margin-bottom: 10px;">
            <el-button type="success" size="mini" @click="setCooling('ON')" :disabled="!manualMode">Cooling (On)</el-button>
            <el-button type="warning" size="mini" @click="setCooling('OFF')" :disabled="!manualMode" style="margin-left: 5px;">Cooling (Off)</el-button>
            <el-button type="success" size="mini" @click="setDehumidifying('ON')" :disabled="!manualMode" style="margin-left: 5px;">Dehumidifying (On)</el-button>
            <el-button type="warning" size="mini" @click="setDehumidifying('OFF')" :disabled="!manualMode" style="margin-left: 5px;">Dehumidifying (Off)</el-button>
          </div>

          <el-button type="primary" @click="viewDeviceData('aircon')">View Data</el-button>

          <div v-if="showAirData" class="device-data-box">
            <h4>Latest Data:</h4>
            <pre>{{ JSON.stringify(airConditionerData, null, 2) }}</pre>
            <el-button type="primary" size="mini" @click="refreshDeviceData('aircon')">Refresh</el-button>
            <el-button type="danger" size="mini" @click="closeDeviceData('aircon')" style="margin-left: 5px;">Close</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 返回按钮固定在左下角 -->
    <el-button class="back-button" type="info" @click="goBack">
      Back to Home
    </el-button>
  </div>
</template>



<script>
import axios from "axios";

export default {
  data() {
    return {
      manualMode: false,
      lightingStatus: "N/A",
      waterHeaterStatus: "N/A",
      heaterButtonText: "Turn On",
      statusMapping: {
        brighter: "BRIGHTER",
        dimmer: "DIMMER",
        off: "OFF",
        on: "ON",
      },
        dialogVisible: false,
        deviceData: {},
        currentDevice: "",
        lightingData: {},
        waterHeaterData: {},
        cameraStatus: "N/A",
        cameraData: {},
        showCameraData: false,
        cameraStream: null,
        showLightingData: false,
        showWaterHeaterData: false,
        coolingStatus: "N/A",
        dehumidifyingStatus: "N/A",
        airConditionerData: {},
        showAirData: false,
        fixedStatus: {
           lighting: null,
           water_heater: null
      }
    };
  },
  methods: {
    toggleManualMode() {
  console.log(`[模式切换] 当前模式: ${this.manualMode ? 'Manual' : 'Auto'}`);

  if (!this.manualMode) {
    // ✅ 切换到自动模式
    console.log("[切换到自动模式] 状态重置为 N/A");

    // 🔄 所有设备状态重置
    this.lightingStatus = "N/A";
    this.waterHeaterStatus = "N/A";
    this.coolingStatus = "N/A";
    this.dehumidifyingStatus = "N/A";
    this.heaterButtonText = "Turn On";

    // 🔄 清除本地存储
    localStorage.setItem("manualMode", "false");
    localStorage.removeItem("lightingStatus");
    localStorage.removeItem("waterHeaterStatus");
    localStorage.removeItem("coolingStatus");
    localStorage.removeItem("dehumidifyingStatus");

    // 🔄 清除固定显示状态
    this.fixedStatus = {
      lighting: null,
      water_heater: null
    };

    // ✅ 同步后端：切换为自动模式
    axios.post("http://localhost:5050/api/device/toggle-mode", {
      manual_mode: "off"
    })
    .then((response) => {
      console.log("[后端同步] 切换为自动模式:", response.data.message);
    })
    .catch((error) => {
      console.error("[错误] 切换到自动模式失败:", error);
    });

  } else {
    // ✅ 切换到手动模式
    console.log("[切换到手动模式] 恢复本地存储的状态");

    // 🔄 恢复灯光与热水器状态
    const lightingState = localStorage.getItem("lightingStatus");
    const heaterState = localStorage.getItem("waterHeaterStatus");

    this.lightingStatus = lightingState ? lightingState : "OFF";
    this.waterHeaterStatus = heaterState ? heaterState : "OFF";
    this.heaterButtonText = this.waterHeaterStatus === "ON" ? "Turn Off" : "Turn On";

    // 🔄 恢复空调 cooling / dehumidifying 状态
    const coolingState = localStorage.getItem("coolingStatus");
    const dehumidifyState = localStorage.getItem("dehumidifyingStatus");

    this.coolingStatus = coolingState ? coolingState : "OFF";
    this.dehumidifyingStatus = dehumidifyState ? dehumidifyState : "OFF";

    // 🔄 写入本地存储
    localStorage.setItem("manualMode", "true");
    localStorage.setItem("lightingStatus", this.lightingStatus);
    localStorage.setItem("waterHeaterStatus", this.waterHeaterStatus);
    localStorage.setItem("coolingStatus", this.coolingStatus);
    localStorage.setItem("dehumidifyingStatus", this.dehumidifyingStatus);

    // 🔄 初始化固定显示状态（用于 View Data）
    this.updateFixedStatus("lighting", this.lightingStatus);
    this.updateFixedStatus("water_heater", this.waterHeaterStatus);

    // ✅ 同步后端：切换为手动模式
    axios.post("http://localhost:5050/api/device/toggle-mode", {
      manual_mode: "on"
    })
    .then((response) => {
      console.log("[后端同步] 切换为手动模式:", response.data.message);
    })
    .catch((error) => {
      console.error("[错误] 切换到手动模式失败:", error);
    });
  }
},

setCooling(state) {
  this.coolingStatus = state;
  localStorage.setItem("coolingStatus", state);
  this.syncCurrentState("aircon", `COOLING_${state}`);
},

setDehumidifying(state) {
  this.dehumidifyingStatus = state;
  localStorage.setItem("dehumidifyingStatus", state);
  this.syncCurrentState("aircon", `DEHUMIDIFYING_${state}`);
},
enableCamera() {
  if (!this.manualMode || this.cameraStatus === "on") return;

  navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
      this.cameraStream = stream;
      this.cameraStatus = "on";

      // 👇 不再强制控制 showCameraData，仅控制摄像头状态
      this.$nextTick(() => {
        const video = this.$refs.cameraVideo;
        if (video) {
          video.srcObject = stream;
          video.play();
        } else {
          console.warn("cameraVideo ref not found — video element not rendered yet.");
        }
      });

      // axios.post("http://localhost:5050/api/device/camera/start");
    })
    .catch((err) => {
      console.error("Failed to enable camera:", err);
    });
},

disableCamera() {
  if (this.cameraStream) {
    this.cameraStream.getTracks().forEach(track => track.stop());
    this.cameraStream = null;
  }

  this.cameraStatus = "off";

  // ✅ 清除视频画面
  if (this.$refs.cameraVideo) {
    this.$refs.cameraVideo.srcObject = null;
  }

  // ❌ 不再关闭 showCameraData，这样 View Data 区块可单独控制
  // axios.post("http://localhost:5050/api/device/camera/stop");
},


viewDeviceData(device) {
  if (device === "camera") {
    axios.get("http://localhost:5050/api/device/camera/manual-state")
      .then((stateRes) => {
        const manual = stateRes.data.manual_override;

        axios.get("http://localhost:5050/api/realtime-db/fps")
          .then((res) => {
            const data = res.data;
            data.status = manual === "on" ? this.cameraStatus : "N/A";
            this.cameraData = data;
            this.showCameraData = true;
          });
      });
    return;
  }

  // ✅ 空调强制使用固定接口路径，避免动态拼接出错
  const url = device === "aircon"
    ? "http://localhost:5050/api/device/aircon/view-data"
    : `http://localhost:5050/api/device/${device}/view-data`;

  axios.get(url)
    .then((response) => {
      const originalData = response.data;

      axios.get(`http://localhost:5050/api/device/${device}/manual-state`)
        .then((stateRes) => {
          const status = stateRes.data.status;
          const manual = stateRes.data.manual_override;

          if (device === "lighting" && manual === "on") {
            this.updateFixedStatus(device, status);
            originalData.status = this.fixedStatus.lighting;
          }

          if (device === "water_heater" && manual === "on") {
            this.updateFixedStatus(device, status);
            originalData.status = this.fixedStatus.water_heater;
          }

          if (device === "aircon" && manual === "on") {
            originalData.cooling_status = this.coolingStatus;
            originalData.dehumidifying_status = this.dehumidifyingStatus;
          }

          if (device === "lighting") {
            this.lightingData = originalData;
            this.showLightingData = true;
          } else if (device === "water_heater") {
            this.waterHeaterData = originalData;
            this.showWaterHeaterData = true;
          } else if (device === "aircon") {
            this.airConditionerData = originalData;
            this.showAirData = true;
          }
        });
    });
},


refreshDeviceData(device) {
  if (device === "camera") {
    this.viewDeviceData("camera");
    return;
  }

  const url = device === "aircon"
    ? "http://localhost:5050/api/device/aircon/view-data"
    : `http://localhost:5050/api/device/${device}/view-data`;

  axios.get(url)
    .then((response) => {
      const refreshed = response.data;

      axios.get(`http://localhost:5050/api/device/${device}/manual-state`)
        .then((res) => {
          const manual = res.data.manual_override;
          const status = res.data.status;

          if (manual === "on") {
            this.updateFixedStatus(device, status);

            if (device === "lighting") {
              refreshed.status = this.fixedStatus.lighting;
            } else if (device === "water_heater") {
              refreshed.status = this.fixedStatus.water_heater;
            } else if (device === "aircon") {
              refreshed.cooling_status = this.coolingStatus;
              refreshed.dehumidifying_status = this.dehumidifyingStatus;
            }
          }

          if (device === "lighting") {
            this.lightingData = refreshed;
          } else if (device === "water_heater") {
            this.waterHeaterData = refreshed;
          } else if (device === "aircon") {
            this.airConditionerData = refreshed;
          }
        });
    });
},
syncLightingStatus() {
  axios.get("http://localhost:5050/api/device/lighting/manual-state")
    .then((res) => {
      const status = res.data.status;
      const manual = res.data.manual_override;
      if (manual === "on") {
        this.updateFixedStatus("lighting", status);
        this.lightingStatus = status;  // ✅ 使用原始状态显示在方框
      }
    });
},

syncWaterHeaterStatus() {
  axios.get("http://localhost:5050/api/device/water_heater/manual-state")
    .then((res) => {
      const status = res.data.status;
      const manual = res.data.manual_override;
      if (manual === "on") {
        this.updateFixedStatus("water_heater", status);
        this.waterHeaterStatus = status;  // ✅ 使用原始状态显示在方框
        this.heaterButtonText = status === "ON" ? "Turn Off" : "Turn On";
      }
    });
},


  syncAirconStatus() {
    axios.get("http://localhost:5050/api/device/aircon/manual-state")
      .then((res) => {
        const manual = res.data.manual_override;
        if (manual === "on") {
          this.coolingStatus = res.data.cooling_status || "ON";
          this.dehumidifyingStatus = res.data.dehumidifying_status || "ON";
        }
      });
  },

updateFixedStatus(device, status) {
  if (device === "lighting") {
    if (status === "BRIGHTER") {
      this.fixedStatus.lighting = "on (Brighter)";
    } else if (status === "DIMMER") {
      this.fixedStatus.lighting = "on (Dimmer)";
    } else if (status === "OFF") {
      this.fixedStatus.lighting = "off";
    }
  } else if (device === "water_heater") {
    if (status === "ON") {
      this.fixedStatus.water_heater = "running";
    } else if (status === "OFF") {
      this.fixedStatus.water_heater = "stopped";
    }
  }
},


closeDeviceData(device) {
  if (device === "lighting") {
    this.showLightingData = false;
  } else if (device === "water_heater") {
    this.showWaterHeaterData = false;
  } else if (device === "camera") {
    this.showCameraData = false;
  } else if (device === "aircon") {
    this.showAirData = false;
  }
},


    controlDevice(device, action) {
      axios
        .post(`http://localhost:5050/api/device/${device}/${action}`)
        .then(() => {
          // 🔥 移除了未使用的 response
          if (device === "lighting") {
            this.lightingStatus = this.statusMapping[action] || "OFF";
          } else if (device === "water_heater") {
            this.waterHeaterStatus = this.statusMapping[action] || "OFF";
          }

          if (this.manualMode) {
            this.syncCurrentState(device, action);
          }
        })
        .catch((error) => {
          console.error(`Failed to control ${device}:`, error);
        });
    },
    syncCurrentState(device, action) {
      axios.post(`http://localhost:5050/api/device/${device}/save-state`, {
        status: action,
        mode: this.manualMode ? "on" : "off"
      })
      .then(() => {
        console.log(`State synced for ${device}: ${action}, Mode: ${this.manualMode ? "Manual" : "Auto"}`);
      })
      .catch((error) => {
        console.error("Failed to sync state:", error);
      });
    },
    toggleHeater() {
      const action = this.waterHeaterStatus === "OFF" || this.waterHeaterStatus === "N/A" ? "on" : "off";
      this.controlDevice("water_heater", action);

      // 切换按钮文字
      this.heaterButtonText = action === "on" ? "Turn Off" : "Turn On";
    },
    goBack() {
      this.$router.push('/home');
    }
  },
  mounted() {
  console.log("[初始化] 同步手动模式和设备状态");

  axios.get("http://localhost:5050/api/device/water_heater/current-status")
    .then((response) => {
      const { manual_mode, status } = response.data;

      // ✅ 恢复模式
      this.manualMode = manual_mode === "on";

      if (!this.manualMode) {
        // 🔄 如果是自动模式
        this.lightingStatus = "N/A";
        this.waterHeaterStatus = "N/A";
        this.coolingStatus = "N/A";
        this.dehumidifyingStatus = "N/A";
        this.heaterButtonText = "Turn On";
      } else {
        // ✅ 自动同步当前手动状态
        this.syncLightingStatus();
        this.syncWaterHeaterStatus();
        this.syncAirconStatus();
      }

      console.log(`[模式同步] 当前模式: ${manual_mode}, 热水器状态: ${status}`);
    })
    .catch((error) => {
      console.error("[错误] 获取设备状态失败: ", error);
    });
},


};
</script>

<style scoped>
.device-control-container {
  padding: 20px;
  min-height: 140vh; /* ✅ 让两行卡片足够展开空间 */
  box-sizing: border-box;
}

.device-grid {
  margin-top: 20px;
}

.back-button {
  position: fixed;
  bottom: 20px;
  left: 20px;
}

/* ✅ 所有设备的数据展示区域 */
.device-data-box {
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 10px;
  margin-top: 10px;
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 13px;
  max-height: 120px;
  overflow-y: auto;
}

/* ✅ 所有普通设备卡片统一高度（包括展开 View Data 后） */
.el-card {
  min-height: 580px; /* ✅ 与摄像头一致，防止点击后撑高或错位 */
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* ✅ 摄像头卡片类名（可单独样式） */
.camera-card {
  min-height: 580px; /* ✅ 与普通设备一致，保持整齐 */
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

/* ✅ 摄像头视频展示区域（高度加大） */
.camera-video-box {
  margin-top: 10px;
  overflow: hidden;
  border: 1px solid #ccc;
  border-radius: 6px;
  height: 360px; /* ✅ 原为320，加大用于完整展示 */
}

/* ✅ 视频填满容器但不拉伸 */
.camera-video-box video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ✅ 响应式顺序（摄像头排在下方） */
@media (min-width: 768px) {
  .camera-col {
    order: 2;
  }
  .heater-col {
    order: 1;
  }
}
</style>








  
  
  
  
  
  
  