<template>
  <div class="login-container">
    <!-- Login Card -->
    <el-card class="login-card" v-if="!showRegister">
      <h2 class="login-title">Smart Home System Login</h2>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="100px">
        <el-form-item label="Username" prop="username">
          <el-input v-model="loginForm.username" placeholder="Enter your username" clearable />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="Enter your password" clearable />
        </el-form-item>
        <div class="login-btns">
          <el-button type="primary" @click="submitLogin" :loading="loading.login">Login</el-button>
          <el-button type="success" @click="openRegister">Register</el-button>
        </div>
      </el-form>
    </el-card>

    <!-- Register Modal -->
    <div class="register-overlay" v-if="showRegister">
      <el-card class="register-card">
        <h2 style="text-align: center">Register New Account</h2>
        <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="130px">
          <el-form-item label="Username" prop="username">
            <el-input v-model="registerForm.username" placeholder="Enter username" clearable />
          </el-form-item>
          <el-form-item label="Password" prop="password">
            <el-input v-model="registerForm.password" type="password" placeholder="Enter password" clearable />
          </el-form-item>
          <el-form-item label="Confirm Password" prop="confirm">
            <el-input v-model="registerForm.confirm" type="password" placeholder="Re-enter password" clearable />
          </el-form-item>
          <el-form-item label="Phone" prop="phone">
            <el-input v-model="registerForm.phone" placeholder="Enter phone number" clearable />
          </el-form-item>
          <el-form-item label="Email" prop="email">
            <el-input v-model="registerForm.email" placeholder="Enter email address" clearable />
          </el-form-item>
          <el-form-item label="ID Number" prop="idNumber">
            <el-input v-model="registerForm.idNumber" placeholder="Enter ID number" clearable />
          </el-form-item>
          <el-form-item label="Home Address" prop="homeAddress">
            <el-input v-model="registerForm.homeAddress" placeholder="Enter home address" clearable />
          </el-form-item>
          <el-form-item label="Company Name" prop="company">
            <el-input v-model="registerForm.company" placeholder="Enter company name" clearable />
          </el-form-item>
          <el-form-item label="Company Address" prop="companyAddress">
            <el-input v-model="registerForm.companyAddress" placeholder="Enter company address" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitRegister" :loading="loading.register">Submit</el-button>
            <el-button @click="closeRegister">Back</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginPage',
  data() {
    return {
      showRegister: false,
      loginForm: { username: '', password: '' },
      registerForm: {
        username: '', password: '', confirm: '', phone: '', email: '',
        idNumber: '', homeAddress: '', company: '', companyAddress: ''
      },
      loading: { login: false, register: false },
      loginRules: {
        username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
        password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
      },
      registerRules: {
        username: [
          { required: true, message: 'Please enter username', trigger: 'blur' },
          { min: 3, max: 20, message: 'Length must be 3-20 characters', trigger: 'blur' },
          { pattern: /^\w+$/, message: 'Only letters, numbers, and _ allowed', trigger: 'blur' }
        ],
        password: [
          { required: true, message: 'Please enter password', trigger: 'blur' },
          { min: 8, message: 'At least 8 characters', trigger: 'blur' },
          { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/, 
            message: 'Must contain uppercase, lowercase, number, and special character', trigger: 'blur' }
        ],
        confirm: [
          { required: true, message: 'Please confirm password', trigger: 'blur' },
          {
            validator: (rule, value, callback) => {
              if (value !== this.registerForm.password) {
                callback(new Error('Passwords do not match'));
              } else {
                callback();
              }
            },
            trigger: 'blur'
          }
        ],
        phone: [
          { required: true, message: 'Please enter phone number', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: 'Invalid phone number format', trigger: 'blur' }
        ],
        email: [
          { required: true, message: 'Please enter email address', trigger: 'blur' },
          { type: 'email', message: 'Invalid email address format', trigger: 'blur' }
        ],
        idNumber: [
          { required: true, message: 'Please enter ID number', trigger: 'blur' },
          { pattern: /^\d{15}(\d{2}[\dxX])?$/, message: 'Invalid ID number format', trigger: 'blur' }
        ],
        homeAddress: [
          { required: true, message: 'Please enter home address', trigger: 'blur' },
          { min: 5, message: 'Home address must be at least 5 characters', trigger: 'blur' }
        ],
        company: [
          { required: true, message: 'Please enter company name', trigger: 'blur' },
          { min: 2, message: 'Company name must be at least 2 characters', trigger: 'blur' }
        ],
        companyAddress: [
          { required: true, message: 'Please enter company address', trigger: 'blur' },
          { min: 5, message: 'Company address must be at least 5 characters', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    // 🚀 这里补充 submitLogin 方法
    async submitLogin() {
      this.loading.login = true;
      try {
        await this.$refs.loginFormRef.validate(); // 验证表单
        const response = await axios.post('http://localhost:5050/login', this.loginForm);
        this.$message.success(response.data.message || 'Login successful');
        localStorage.setItem('loggedIn', 'true');
        localStorage.setItem('username', this.loginForm.username);
        this.$router.push('/home');
      } catch (err) {
        console.error("❌ 登录失败:", err.message);
        this.$message.error(err.response?.data?.message || 'Login failed');
      } finally {
        this.loading.login = false;
      }
    },
    openRegister() {
      this.showRegister = true;
      this.$nextTick(() => {
        this.$refs.registerFormRef.resetFields();
      });
    },
    closeRegister() {
      this.showRegister = false;
      this.$refs.registerFormRef.resetFields();
    },
    async submitRegister() {
      this.loading.register = true;
      try {
        // 验证表单是否通过
        const valid = await this.$refs.registerFormRef.validate();
        if (!valid) {
          console.warn("❌ 表单验证未通过，阻止提交");
          this.loading.register = false;
          return;
        }

        console.log("👉 提交的数据:", this.registerForm);

        // 发送请求
        const response = await axios.post('http://localhost:5050/register', this.registerForm);

        console.log("✅ 注册成功，后端返回:", response.data);

        this.$message.success(response.data.message || 'Registration successful');
        this.closeRegister();
      } catch (err) {
        if (err.response) {
          console.error("❌ 后端返回的错误信息:", err.response.data);
          this.$message.error(err.response.data.message || 'Registration failed');
        } else {
          console.error("❌ 未知错误:", err.message);
        }
      } finally {
        this.loading.register = false;
      }
    }
  }
};
</script>

<style scoped>
/* 登录和注册容器样式 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f0f2f5;
  position: relative;
}

/* 登录卡片样式 */
.login-card {
  width: 420px;
  padding: 30px 20px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  z-index: 1;
  transition: all 0.3s ease;
}

.login-title {
  text-align: center;
  margin-bottom: 20px;
}

.login-btns {
  display: flex;
  justify-content: space-around;
}

/* 注册卡片的弹出动画 */
.register-overlay {
  position: absolute;
  width: 620px;
  max-width: 90%;
  background: #fff;
  z-index: 2;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease forwards;
}

/* 注册卡片内部的样式 */
.register-card {
  width: 100%;
}

/* 弹出动画 */
@keyframes slideIn {
  0% {
    transform: translateY(-20px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 按钮 hover 效果 */
.el-button {
  transition: background-color 0.3s;
}

.el-button:hover {
  background-color: #409EFF !important;
  color: white !important;
}

/* 🔥 优化后的错误提示样式 */
.el-form-item__error {
  color: #f56c6c !important;
  font-size: 13px;
  margin-top: 3px;
  font-weight: 500;
  display: flex;
  align-items: center;
}

/* 🚀 增加一个小警告图标 */
.el-form-item__error::before {
  content: "⚠️ ";
  margin-right: 5px;
}

/* 🔥 输入框的错误状态显示更清晰 */
.el-input.is-error input {
  border-color: #f56c6c !important;
  background-color: #fff5f5 !important;
  box-shadow: 0 0 5px rgba(245, 108, 108, 0.3);
}

/* 🌟 鼠标悬浮时的错误状态效果 */
.el-input.is-error input:hover {
  border-color: #e53e3e !important;
}

/* ✅ 修正输入框焦点状态 */
.el-input input:focus {
  border-color: #409eff !important;
  box-shadow: 0 0 5px rgba(64, 158, 255, 0.3);
}

/* 对小屏幕的适配 */
@media (max-width: 768px) {
  .login-card {
    width: 90%;
  }

  .register-overlay {
    width: 90%;
  }
}
</style>