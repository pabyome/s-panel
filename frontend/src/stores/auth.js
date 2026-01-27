import { defineStore } from 'pinia';
import axios from 'axios';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null);
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));

  const isAuthenticated = computed(() => !!token.value);

  async function fetchCurrentUser() {
    try {
      const response = await axios.get('/api/v1/auth/me');
      user.value = response.data;
      localStorage.setItem('user', JSON.stringify(user.value));
    } catch (error) {
      console.error('Failed to fetch user:', error);
      // If we can't fetch user, token might be invalid
      if (error.response?.status === 401) {
        logout();
      }
    }
  }

  async function login(username, password) {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post('/api/v1/auth/login', formData);
      const { access_token, token_type } = response.data;

      token.value = access_token;
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      localStorage.setItem('token', access_token);

      // Fetch full user details from /me endpoint
      await fetchCurrentUser();

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
    // Fetch fresh user data on app init if we have a token
    fetchCurrentUser();
  }

  return { token, user, isAuthenticated, login, logout, fetchCurrentUser };
});
