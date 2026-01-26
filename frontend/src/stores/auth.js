import { defineStore } from 'pinia';
import axios from 'axios';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null);
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));

  const isAuthenticated = computed(() => !!token.value);

  async function login(username, password) {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post('/api/v1/auth/login', formData);
      const { access_token, token_type } = response.data;

      token.value = access_token;
      // For now, simpler user object. In real app, might decode JWT or fetch /me
      user.value = { username };

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user.value));

      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
  }

  // Initialize axios header if token exists
  if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
  }

  return { token, user, isAuthenticated, login, logout };
});
