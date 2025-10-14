<template>
	<div>
		<BaseMap :center="[39.9042, 116.4074]" :zoom="11" :fullScreen="true" :offsetTop="navbarHeight" />
	</div>
</template>

<script>
import BaseMap from '../components/map/BaseMap.vue'

export default {
	name: 'Home',
	components: { BaseMap },
	data() {
		return { navbarHeight: 56 } // Bootstrap 默认导航高度，可根据实际调整
	}
}
</script>
