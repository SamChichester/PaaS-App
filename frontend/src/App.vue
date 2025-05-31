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
      const response = await axios.get("http://localhost:5000/me", { withCredentials: true })
      console.log(response)
      this.authorized = response.data.authorized
      if (this.authorized) {
        this.username = response.data.username
        this.fetchRepos()
      }
    },
    login() {
      window.location.href = "http://localhost:5000/login/github?next=http://localhost:5173"
    },
    logout() {
      window.location.href = "http://localhost:5000/logout"
    },
    async fetchRepos() {
      const response = await axios.get("http://localhost:5000/repos",  { withCredentials: true })
      this.repos = response.data
    },
    async deploy(repoUrl) {
      const response = await axios.post(
        "http://localhost:5000/deploy",
        { repoUrl: repoUrl },
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