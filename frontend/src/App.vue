<template>
	<div id="app">
		<nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
			<div class="container-fluid">
				<a class="navbar-brand" href="#/">简途</a>
				<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
					<span class="navbar-toggler-icon"></span>
				</button>
				<div class="collapse navbar-collapse" id="navbarNav">
					<ul class="navbar-nav">
						<li class="nav-item"><router-link class="nav-link" to="/">首页</router-link></li>
						<li class="nav-item"><router-link class="nav-link" to="/place">地点查询</router-link></li>
						<li class="nav-item"><router-link class="nav-link" to="/recommendation">推荐</router-link></li>
						<li class="nav-item"><router-link class="nav-link" to="/route">路径规划</router-link></li>
						<li class="nav-item"><router-link class="nav-link" to="/diary">旅行日记</router-link></li>
					</ul>
				</div>
			</div>
		</nav>
		<main class="container py-3">
			<router-view />
		</main>
	</div>
  
</template>

<script>
export default {
	name: 'App'
}
</script>

<style>
html, body, #app {
	height: 100%;
}
</style>
