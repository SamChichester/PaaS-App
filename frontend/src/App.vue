<template>
  <div>
    <h1>PaaS Deployment</h1>
    <button v-if="!authorized" @click="login">Login with GitHub</button>

    <div v-else>
      <h2>Welcome, {{ username }}</h2>
      <h3>Your Repositories:</h3>
      <ul>
        <li v-for="repo in repos" :key="repo.id">
          {{ repo.name }}
          <button @click="deploy(repo.clone_url)">Deploy</button>
        </li>
      </ul>
      <button @click="logout">Logout</button>
    </div>

    <div v-if="output">
      <h3>Deployment Output:</h3>
      <pre>{{ output }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      authorized: false,
      username: "",
      repos: [],
      output: null
    }
  },
  methods: {
    async checkAuth() {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/me`, { withCredentials: true })
      console.log(response)
      this.authorized = response.data.authorized
      if (this.authorized) {
        this.username = response.data.username
        this.fetchRepos()
      }
    },
    login() {
      window.location.href = `${import.meta.env.VITE_API_URL}/login/github?next=${import.meta.env.VITE_APP_URL}`
    },
    logout() {
      window.location.href = `${import.meta.env.VITE_API_URL}/logout`
    },
    async fetchRepos() {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/repos`,  { withCredentials: true })
      this.repos = response.data
    },
    async deploy(repoUrl) {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/deploy`,
        { repo_url: repoUrl },
        { withCredentials: true }
      )
      this.output = response.data.stdout || response.data.stderr
    },
  },
  mounted() {
    this.checkAuth()
  }
}
</script>