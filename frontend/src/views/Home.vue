<template>
	<div class="h-[calc(100vh-64px)] flex flex-col md:flex-row bg-gray-50 relative">
		<!-- 左侧功能面板 -->
		<div class="w-full md:w-[400px] bg-white border-r border-gray-200 flex flex-col shadow-xl z-20 h-full">
		<!-- 顶部 Tab 切换 -->
		<div class="flex border-b border-gray-100 bg-white shrink-0">
			<button 
				v-for="tab in tabs" 
				:key="tab.id"
				@click="switchTab(tab.id)"
				class="flex-1 py-3 text-sm font-semibold flex items-center justify-center gap-2 transition-colors"
				:class="activeTab === tab.id ? 'text-brand-600 border-b-2 border-brand-500 bg-brand-50/50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'"
			>
				<i :class="tab.icon"></i> {{ tab.name }}
			</button>
		</div>			<!-- 内容区域 -->
			<div class="flex-1 overflow-y-auto bg-gray-50/50 p-4">
				<!-- 附近 -->
				<div v-if="activeTab==='place'" class="space-y-4">
					<div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 space-y-3">
						<div class="grid grid-cols-2 gap-3">
							<div>
								<label class="block text-xs font-medium text-gray-500 mb-1">纬度</label>
								<input v-model.number="place.lat" type="number" step="0.0001" class="w-full rounded-lg border-gray-200 text-sm focus:ring-brand-500 focus:border-brand-500" />
							</div>
							<div>
								<label class="block text-xs font-medium text-gray-500 mb-1">经度</label>
								<input v-model.number="place.lon" type="number" step="0.0001" class="w-full rounded-lg border-gray-200 text-sm focus:ring-brand-500 focus:border-brand-500" />
							</div>
						</div>
						<div class="grid grid-cols-2 gap-3">
							<div>
								<label class="block text-xs font-medium text-gray-500 mb-1">半径(km)</label>
								<input v-model.number="place.radius" type="number" min="1" max="50" class="w-full rounded-lg border-gray-200 text-sm focus:ring-brand-500 focus:border-brand-500" />
							</div>
							<div>
								<label class="block text-xs font-medium text-gray-500 mb-1">类别</label>
								<select v-model="place.category" class="w-full rounded-lg border-gray-200 text-sm focus:ring-brand-500 focus:border-brand-500">
									<option value="">全部</option>
									<option v-for="c in place.categories" :key="c" :value="c">{{ c }}</option>
								</select>
							</div>
						</div>
						<div class="flex gap-2 pt-2">
							<button class="flex-1 bg-brand-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors flex items-center justify-center gap-2" @click="loadNearby">
								<span v-if="place.loading" class="spinner-border spinner-border-sm w-3 h-3"></span>
								<i class="bi bi-search"></i> 查询附近
							</button>
							<button class="px-3 py-2 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50" @click="locate" title="定位"><i class="bi bi-geo-alt"></i></button>
							<button class="px-3 py-2 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50" @click="syncMapCenter" title="取地图中心"><i class="bi bi-crosshair"></i></button>
						</div>
					</div>

					<div class="space-y-2">
						<div v-if="!place.loading && place.list.length===0" class="text-center py-8 text-gray-400">
							<i class="bi bi-inbox text-4xl mb-2 block"></i>
							<p class="text-sm">暂无数据</p>
						</div>
						<button v-for="p in place.list" :key="p.id || p.attraction_id || p.name" 
							class="w-full text-left bg-white p-3 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group"
							:class="{ 'ring-2 ring-brand-500 border-transparent': selectedId === (p.id || p.attraction_id) }"
							@click="focusPlace(p)">
							<div class="flex justify-between items-start mb-1">
								<h4 class="font-bold text-gray-800 group-hover:text-brand-600 transition-colors">{{ p.name }}</h4>
								<span v-if="p.distance_km !== undefined" class="text-xs font-medium text-brand-600 bg-brand-50 px-2 py-0.5 rounded-full">{{ p.distance_km }} km</span>
							</div>
							<div class="text-xs text-gray-500 flex items-center gap-2">
								<span class="bg-gray-100 px-2 py-0.5 rounded">{{ p.category || p.type || '未知' }}</span>
							</div>
						</button>
					</div>
				</div>

				<!-- 推荐 -->
				<div v-else-if="activeTab==='recommend'" class="space-y-4">
					<div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 space-y-3">
						<div class="relative">
							<input v-model.trim="recommend.query" type="text" class="w-full pl-9 pr-4 py-2 rounded-lg border-gray-200 text-sm focus:ring-brand-500 focus:border-brand-500" placeholder="搜索关键词..." @keyup.enter="refreshRecommend" />
							<i class="bi bi-search absolute left-3 top-2.5 text-gray-400"></i>
						</div>
						
						<div class="grid grid-cols-3 gap-2">
							<select v-model="recommend.prefs.algorithm" class="rounded-lg border-gray-200 text-xs focus:ring-brand-500 focus:border-brand-500 py-1.5">
								<option value="content_based">内容推荐</option>
								<option value="collaborative">协同过滤</option>
							</select>
							<select v-model="recommend.prefs.sort_by" class="rounded-lg border-gray-200 text-xs focus:ring-brand-500 focus:border-brand-500 py-1.5">
								<option value="score">综合排序</option>
								<option value="popularity">热度优先</option>
								<option value="rating">评分优先</option>
							</select>
							<input v-model.number="recommend.prefs.top_n" type="number" min="1" max="100" class="rounded-lg border-gray-200 text-xs focus:ring-brand-500 focus:border-brand-500 py-1.5" placeholder="Top N" />
						</div>

						<div class="flex justify-between items-center pt-1">
							<button class="text-xs text-brand-600 font-medium hover:text-brand-700 flex items-center gap-1" @click="recommend.showAdv = !recommend.showAdv">
								{{ recommend.showAdv ? '收起筛选' : '更多筛选' }} <i class="bi" :class="recommend.showAdv ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
							</button>
							<button class="bg-brand-600 text-white px-4 py-1.5 rounded-lg text-xs font-medium hover:bg-brand-700 transition-colors" @click="refreshRecommend">
								应用筛选
							</button>
						</div>

						<div v-if="recommend.showAdv" class="pt-2 border-t border-gray-100">
							<div class="text-xs text-gray-500 mb-2">类别筛选</div>
							<div class="flex flex-wrap gap-2">
								<label class="inline-flex items-center px-2 py-1 rounded-md bg-gray-50 border border-gray-200 cursor-pointer hover:bg-gray-100" v-for="c in recommend.categories" :key="c">
									<input class="form-checkbox h-3 w-3 text-brand-600 rounded border-gray-300 focus:ring-brand-500" type="checkbox" :value="c" v-model="recommend.prefs.categories" /> 
									<span class="ml-1.5 text-xs text-gray-700">{{ c }}</span>
								</label>
							</div>
						</div>
					</div>

					<div class="space-y-2">
						<div v-if="!recommend.loading && recommend.list.length===0" class="text-center py-8 text-gray-400">
							<i class="bi bi-inbox text-4xl mb-2 block"></i>
							<p class="text-sm">暂无推荐数据</p>
						</div>
						<button v-for="r in recommend.list" :key="getId(r)" 
							class="w-full text-left bg-white p-3 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group"
							:class="{ 'ring-2 ring-brand-500 border-transparent': selectedId === getId(r) }"
							@click="focusRecommend(r)">
							<div class="flex justify-between items-start mb-1">
								<h4 class="font-bold text-gray-800 group-hover:text-brand-600 transition-colors">{{ r.name }}</h4>
								<div class="flex items-center gap-1">
									<span v-if="r.rating" class="flex items-center gap-1 text-xs font-bold text-yellow-600 bg-yellow-50 px-1.5 py-0.5 rounded">
										<i class="bi bi-star-fill text-[10px]"></i> {{ r.rating }}
									</span>
									<span v-else-if="r.popularity" class="flex items-center gap-1 text-xs font-bold text-red-600 bg-red-50 px-1.5 py-0.5 rounded">
										<i class="bi bi-fire text-[10px]"></i> {{ r.popularity }}
									</span>
								</div>
							</div>
							<div class="text-xs text-gray-500">
								<span class="bg-gray-100 px-2 py-0.5 rounded">{{ r.type || r.category || '未知' }}</span>
							</div>
						</button>
					</div>
				</div>

				<!-- 路径规划 -->
				<div v-else-if="activeTab==='route'" class="space-y-4">
					<div class="bg-gradient-to-r from-brand-600 via-brand-500 to-brand-400 text-white rounded-2xl p-5 shadow-lg">
						<div class="flex flex-col gap-2">
							<p class="text-sm text-white/80">智能行程概览</p>
							<div class="flex flex-wrap gap-6 items-center">
								<div>
									<p class="text-[13px] text-white/70">已选站点</p>
									<p class="text-3xl font-semibold">{{ routeStats.points }}</p>
								</div>
								<div>
									<p class="text-[13px] text-white/70">连接段数</p>
									<p class="text-3xl font-semibold">{{ routeStats.segments }}</p>
								</div>
								<div>
									<p class="text-[13px] text-white/70">估算距离</p>
									<p class="text-3xl font-semibold">{{ routeStats.distanceText }}</p>
								</div>
							</div>
							<p class="text-xs text-white/80">提示：点击地图添加站点，使用下方的模式切换开关选择"顺序访问"或"智能优化"模式。</p>
						</div>
					</div>

					<div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 space-y-4">
						<div class="flex flex-col gap-1">
							<h4 class="text-base font-semibold text-gray-900">搜索或添加地点</h4>
							<p class="text-sm text-gray-500">输入任意地点名称即可从开放地图检索，或开启“地图选点”直接点击地图。</p>
						</div>
						<div class="flex flex-col gap-2 sm:flex-row">
							<div class="relative flex-1">
								<i class="bi bi-search absolute left-3 top-2.5 text-gray-400"></i>
								<input v-model.trim="routeSearch.query" @keyup.enter="searchRoutePlaces" type="text" class="w-full pl-9 pr-4 py-2 rounded-lg border-gray-200 text-sm focus:ring-brand-500 focus:border-brand-500" placeholder="例如：杭州西湖 / 成都火车站" />
							</div>
							<button class="px-4 py-2.5 rounded-lg text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 transition disabled:opacity-60" :disabled="routeSearch.loading || !routeSearch.query" @click="searchRoutePlaces">
								<span v-if="routeSearch.loading" class="inline-flex items-center gap-2"><span class="animate-spin w-4 h-4 border-2 border-white/50 border-t-transparent rounded-full"></span> 搜索中</span>
								<span v-else>开始搜索</span>
							</button>
						</div>
						<p class="text-xs text-gray-400">提示：可以通过“预览”定位到地图，再点击“加入路线”将该点放入路径列表。</p>
						<div v-if="routeSearch.error" class="text-xs text-rose-600 bg-rose-50 border border-rose-100 px-3 py-2 rounded-lg">{{ routeSearch.error }}</div>
						<div v-if="routeSearch.loading" class="text-sm text-gray-500 flex items-center gap-2">
							<span class="animate-spin w-4 h-4 border-2 border-gray-200 border-t-transparent rounded-full"></span>
							从开放地图检索地点中...
						</div>
						<div v-else class="space-y-2">
							<div v-if="routeSearch.results.length === 0" class="text-xs text-gray-400">
								<span v-if="routeSearch.query">暂无匹配结果，换个关键词试试。</span>
								<span v-else>输入城市、景点、地址等关键词来查找候选点。</span>
							</div>
							<div v-else>
								<div v-for="place in routeSearch.results" :key="place.id" class="flex flex-col gap-2 p-3 rounded-xl border border-gray-100 bg-gray-50/60">
									<div>
										<p class="text-sm font-semibold text-gray-900">{{ place.title }}</p>
										<p class="text-xs text-gray-500 line-clamp-2">{{ place.subtitle }}</p>
									</div>
									<div class="flex flex-wrap gap-2 text-xs">
										<button class="px-3 py-1.5 rounded-full border border-gray-200 text-gray-600 hover:bg-white" @click="focusRouteCandidate(place)">
											<i class="bi bi-geo"></i> 预览
										</button>
										<button class="px-3 py-1.5 rounded-full bg-brand-600 text-white font-medium hover:bg-brand-700" @click="addRoutePointFromSearch(place)">
											<i class="bi bi-plus-circle"></i> 加入路线
										</button>
									</div>
								</div>
							</div>
						</div>
					</div>

					<div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 space-y-4">
						<div class="flex flex-col gap-1">
							<h4 class="text-base font-semibold text-gray-900">标记路线</h4>
							<p class="text-sm text-gray-500">在左侧地图选择旅程关键节点，也可以手动撤销、反转或清空。</p>
						</div>
						
						<!-- 路径规划模式选择 -->
						<div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-3 border border-blue-100">
							<div class="flex items-center justify-between mb-2">
								<label class="text-sm font-semibold text-gray-700">路径规划模式</label>
								<button 
									@click="optimizeMode = !optimizeMode"
									class="px-3 py-1 rounded-lg text-xs font-bold transition-all"
									:class="optimizeMode ? 'bg-amber-500 text-white shadow-md' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'"
								>
									{{ optimizeMode ? '智能优化' : '顺序访问' }}
								</button>
							</div>
							<p class="text-xs text-gray-600">
								<span v-if="optimizeMode">
									<i class="bi bi-stars text-amber-500"></i> 
									<strong>智能优化模式：</strong>系统会自动计算最优访问顺序，第一个点为起点，其余点按最短路径排序
								</span>
								<span v-else>
									<i class="bi bi-list-ol text-blue-500"></i> 
									<strong>顺序访问模式：</strong>严格按照您添加点的顺序进行路径规划
								</span>
							</p>
						</div>
						
						<div class="flex flex-wrap gap-2">
							<button class="flex-1 min-w-[180px] py-2.5 rounded-xl text-sm font-semibold transition-colors flex items-center justify-center gap-2"
								:class="routeMode ? 'bg-rose-50 text-rose-600 border border-rose-200 hover:bg-rose-100' : 'bg-brand-600 text-white hover:bg-brand-700'"
								@click="toggleRouteMode">
								<i class="bi" :class="routeMode ? 'bi-stop-circle' : 'bi-geo-alt'"></i>
								{{ routeMode ? '停止添加点' : '开始在地图选点' }}
							</button>
							<button class="px-3 py-2 rounded-xl border border-gray-200 text-xs font-semibold text-gray-600 hover:bg-gray-50 disabled:opacity-50" @click="undoRoute" :disabled="routeMarkers.length===0">撤销</button>
							<button class="px-3 py-2 rounded-xl border border-gray-200 text-xs font-semibold text-gray-600 hover:bg-gray-50 disabled:opacity-50" @click="reverseRoute" :disabled="routeMarkers.length<2">反向</button>
							<button class="px-3 py-2 rounded-xl border border-gray-200 text-xs font-semibold text-gray-600 hover:bg-gray-50 disabled:opacity-50" @click="clearRoute" :disabled="routeMarkers.length===0">清空</button>
						</div>
						<button class="w-full bg-brand-50 text-brand-700 border border-brand-200 py-2.5 rounded-xl text-sm font-semibold hover:bg-brand-100 transition flex items-center justify-center gap-2 disabled:opacity-50" 
							@click="planSimpleRoute" :disabled="routeMarkers.length<2 || planning">
							<span v-if="planning" class="inline-flex items-center gap-2"><span class="animate-spin w-4 h-4 border-2 border-brand-200 border-t-transparent rounded-full"></span>规划中</span>
							<span v-else><i class="bi bi-sign-turn-right"></i> 计算路线</span>
						</button>
					</div>

					<div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
						<div class="bg-white rounded-2xl border border-gray-100 shadow-sm">
							<div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
								<h4 class="text-base font-semibold text-gray-900">路线时间线</h4>
								<span class="text-xs text-gray-400">{{ routeMarkers.length }} 个站点</span>
							</div>
							<div v-if="routeMarkers.length" class="px-5 py-4 space-y-4">
								<div v-for="(p, i) in routeMarkers" :key="i" class="flex gap-4">
									<div class="flex flex-col items-center">
										<span class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 font-semibold text-sm flex items-center justify-center">{{ i + 1 }}</span>
										<div v-if="i < routeMarkers.length - 1" class="flex-1 w-px bg-gray-100 mt-1"></div>
									</div>
									<div class="flex-1">
										<p class="text-sm font-semibold text-gray-900 flex items-center gap-2">
											{{ p.label || (`坐标 ${p.latitude.toFixed(4)}, ${p.longitude.toFixed(4)}`) }}
											<span v-if="p.source" class="text-[11px] font-medium px-2 py-0.5 rounded-full" :class="p.source === 'search' ? 'bg-brand-50 text-brand-600' : 'bg-gray-100 text-gray-500'">{{ p.source === 'search' ? '搜索' : '地图' }}</span>
										</p>
										<p class="text-xs text-gray-500 mt-1">坐标 {{ p.latitude.toFixed(4) }}, {{ p.longitude.toFixed(4) }}</p>
										<p v-if="p.meta?.subtitle" class="text-[11px] text-gray-400 mt-1 line-clamp-2">{{ p.meta.subtitle }}</p>
									</div>
								</div>
							</div>
							<div v-else class="px-5 py-10 text-center text-gray-400 text-sm">
								<i class="bi bi-map text-3xl mb-2 block"></i>
								还没有路线点，先在地图上点选吧
							</div>
						</div>

						<div class="space-y-4">
							<div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 space-y-4">
								<div class="flex items-center justify-between">
									<h4 class="text-base font-semibold text-gray-900">路线分析</h4>
									<span class="text-xs text-gray-400">快速评估</span>
								</div>
								<div class="grid grid-cols-3 gap-3 text-center">
									<div class="rounded-xl bg-gray-50 py-3">
										<p class="text-[11px] text-gray-500">站点</p>
										<p class="text-xl font-semibold text-gray-900">{{ routeStats.points }}</p>
									</div>
									<div class="rounded-xl bg-gray-50 py-3">
										<p class="text-[11px] text-gray-500">连接段</p>
										<p class="text-xl font-semibold text-gray-900">{{ routeStats.segments }}</p>
									</div>
									<div class="rounded-xl bg-gray-50 py-3">
										<p class="text-[11px] text-gray-500">距离 (km)</p>
										<p class="text-xl font-semibold text-gray-900">{{ routeStats.distanceLabel }}</p>
									</div>
								</div>
								<p class="text-sm text-gray-500" v-if="routeInfo">系统根据起止点返回的简易里程估算，后续可接入更精确的 OSRM/高德路线。</p>
								<p class="text-sm text-gray-400" v-else>计算路线后，将在这里展示距离等关键信息。</p>
							</div>
							<div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
								<h4 class="text-base font-semibold text-gray-900 mb-3">行程建议</h4>
								<ul class="space-y-2 text-sm text-gray-500">
									<li class="flex items-start gap-2"><i class="bi bi-check-circle-fill text-brand-500 mt-0.5"></i> 勾画不少于 3 个 waypoint，可生成更稳定的行程节奏。</li>
									<li class="flex items-start gap-2"><i class="bi bi-check-circle-fill text-brand-500 mt-0.5"></i> 通过“反向”快速调整出发/抵达次序，便于多城市串联。</li>
									<li class="flex items-start gap-2"><i class="bi bi-check-circle-fill text-brand-500 mt-0.5"></i> 结合日记坐标，可一键回顾曾经路线并纳入新的旅程。</li>
								</ul>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- 地图区域 -->
		<div class="flex-1 h-full relative z-0">
			<BaseMap
				ref="baseMap"
				:center="mapCenter"
				:zoom="11"
				:full-screen="true"
				:offset-top="0"
				:markers="markers"
				:selected-id="selectedId"
				:route-mode="activeTab === 'route' && routeMode"
				:route-markers="routeMarkers"
				:road-path="roadPathCoords"
				@marker-click="onMarkerClick"
				@location-update="onLocationUpdate"
				@route-point-add="onRoutePointAdd"
				@map-click="onMapClick"
			/>
			
			<!-- 地图上的浮动按钮 -->
			<div class="absolute top-4 right-4 flex flex-col gap-2 z-[400]">
				<button class="bg-white p-2 rounded-lg shadow-md text-gray-600 hover:text-brand-600 hover:bg-gray-50 transition-colors" @click="locate" title="定位">
					<i class="bi bi-crosshair text-xl"></i>
				</button>
				<button class="bg-white p-2 rounded-lg shadow-md text-gray-600 hover:text-brand-600 hover:bg-gray-50 transition-colors" @click="goLogin" title="登录" v-if="!isLoggedIn">
					<i class="bi bi-box-arrow-in-right text-xl"></i>
				</button>
			</div>
		</div>

		<!-- 路线结果弹窗 -->
		<div 
			v-if="showRouteResult" 
			class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[1000] flex items-center justify-center p-4"
			@click.self="showRouteResult = false"
		>
			<div class="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden animate-[slideUp_0.3s_ease-out]">
				<!-- 弹窗头部 -->
				<div class="px-6 py-5 bg-gradient-to-r from-brand-500 to-brand-600 text-white">
					<div class="flex items-center justify-between">
						<div>
							<h2 class="text-2xl font-bold flex items-center gap-2">
								<i class="bi bi-route"></i>
								行程路线
							</h2>
							<p class="text-brand-100 text-sm mt-1">为您规划的最佳旅行路线</p>
						</div>
						<button 
							@click="showRouteResult = false"
							class="w-10 h-10 rounded-full bg-white/20 hover:bg-white/30 transition-colors flex items-center justify-center"
						>
							<i class="bi bi-x-lg text-xl"></i>
						</button>
					</div>
				</div>

				<!-- 路线统计卡片 -->
				<div class="px-6 py-4 bg-gradient-to-br from-brand-50 to-blue-50 border-b border-brand-100">
					<div class="grid grid-cols-3 gap-4">
						<div class="bg-white rounded-xl p-4 shadow-sm text-center">
							<div class="text-3xl font-bold text-brand-600">{{ routeStats.points }}</div>
							<div class="text-xs text-gray-500 mt-1">个站点</div>
						</div>
						<div class="bg-white rounded-xl p-4 shadow-sm text-center">
							<div class="text-3xl font-bold text-brand-600">{{ routeStats.distanceLabel }}</div>
							<div class="text-xs text-gray-500 mt-1">总里程 (km)</div>
						</div>
						<div class="bg-white rounded-xl p-4 shadow-sm text-center">
							<div class="text-3xl font-bold text-brand-600">{{ estimatedTime }}</div>
							<div class="text-xs text-gray-500 mt-1">预计耗时</div>
						</div>
					</div>
				</div>

				<!-- 路线时间线 -->
				<div class="px-6 py-6 overflow-y-auto max-h-[calc(90vh-320px)]">
					<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
						<i class="bi bi-signpost-2"></i>
						详细行程
					</h3>
					
					<div class="space-y-6">
						<div v-for="(point, index) in routeMarkers" :key="index" class="flex gap-4 relative">
							<!-- 时间线 -->
							<div class="flex flex-col items-center relative">
								<!-- 站点序号 -->
								<div class="relative z-10">
									<div 
										class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg shadow-lg"
										:class="index === 0 ? 'bg-green-500 text-white' : index === routeMarkers.length - 1 ? 'bg-red-500 text-white' : 'bg-brand-500 text-white'"
									>
										{{ index + 1 }}
									</div>
									<!-- 起点/终点标签 -->
									<div 
										v-if="index === 0 || index === routeMarkers.length - 1"
										class="absolute -bottom-5 left-1/2 transform -translate-x-1/2 whitespace-nowrap"
									>
										<span 
											class="text-[10px] font-semibold px-2 py-0.5 rounded-full"
											:class="index === 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
										>
											{{ index === 0 ? '起点' : '终点' }}
										</span>
									</div>
								</div>
								
								<!-- 连接线 -->
								<div 
									v-if="index < routeMarkers.length - 1" 
									class="flex-1 w-1 bg-gradient-to-b from-brand-300 to-brand-200 my-2 min-h-[60px]"
								></div>
							</div>

							<!-- 站点信息 -->
							<div class="flex-1 pb-6">
								<div class="bg-white rounded-xl border-2 border-gray-100 hover:border-brand-200 transition-all p-4 shadow-sm hover:shadow-md">
									<!-- 站点名称 -->
									<div class="flex items-start justify-between mb-2">
										<div class="flex-1">
											<h4 class="text-lg font-bold text-gray-900 flex items-center gap-2">
												{{ point.label || `站点 ${index + 1}` }}
												<span 
													v-if="point.source" 
													class="text-[10px] font-medium px-2 py-0.5 rounded-full"
													:class="point.source === 'search' ? 'bg-blue-50 text-blue-600' : 'bg-gray-100 text-gray-600'"
												>
													{{ point.source === 'search' ? '搜索添加' : '地图选点' }}
												</span>
											</h4>
											<p v-if="point.meta?.subtitle" class="text-sm text-gray-500 mt-1">
												{{ point.meta.subtitle }}
											</p>
										</div>
									</div>

									<!-- 坐标信息 -->
									<div class="flex items-center gap-2 text-xs text-gray-400 font-mono mb-3">
										<i class="bi bi-geo-alt"></i>
										<span>{{ point.latitude.toFixed(6) }}, {{ point.longitude.toFixed(6) }}</span>
									</div>

									<!-- 到下一站的距离 -->
									<div v-if="index < routeMarkers.length - 1" class="mt-3 pt-3 border-t border-gray-100">
										<div class="flex items-center gap-2 text-sm">
											<i class="bi bi-arrow-down-circle text-brand-500"></i>
											<span class="text-gray-600">到下一站</span>
											<span class="ml-auto font-semibold text-brand-600">
												{{ getSegmentDistance(index).toFixed(2) }} km
											</span>
											<span class="text-gray-400">·</span>
											<span class="text-gray-500">约 {{ getSegmentTime(index) }}</span>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- 弹窗底部：操作按钮 -->
				<div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between gap-3">
					<div class="flex items-center gap-2 text-xs text-gray-500">
						<i class="bi bi-info-circle"></i>
						<span>路线已在地图上展示</span>
					</div>
					<div class="flex items-center gap-2">
						<button 
							@click="exportRoute"
							class="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 transition-colors text-sm font-medium flex items-center gap-2"
						>
							<i class="bi bi-download"></i>
							导出路线
						</button>
						<button 
							@click="showRouteResult = false"
							class="px-6 py-2 rounded-lg bg-brand-600 text-white hover:bg-brand-700 transition-colors text-sm font-medium flex items-center gap-2"
						>
							<i class="bi bi-check-circle"></i>
							确定
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import BaseMap from '../components/map/BaseMap.vue'
import { fetchNearbyPlaces, fetchCategories } from '../api/place'
import { fetchRecommendations, searchRecommendations } from '../api/recommendation'
import { planSimple } from '../api/route'
import { searchPlaces } from '../api/geocode'

export default {
	name: 'Home',
	components: { BaseMap },
	data() {
		return {
			tabs: [
				{ id: 'place', name: '附近', icon: 'bi-geo-alt' },
				{ id: 'recommend', name: '推荐', icon: 'bi-stars' },
				{ id: 'route', name: '路径', icon: 'bi-sign-turn-right' }
			],
			activeTab: 'place',
			mapCenter: [39.9042, 116.4074],
			selectedId: null,
			// 路径
			routeMode: false,
			routeMarkers: [],
			routeInfo: null,
			planning: false,
			optimizeMode: false, // false=顺序模式, true=优化模式
			showRouteResult: false, // 路线结果弹窗
			// 附近
			place: { lat: 39.9042, lon: 116.4074, radius: 5, category: '', categories: [], list: [], loading: false },
			// 推荐
			recommend: { query: '', list: [], loading: false, showAdv: false, categories: ['历史景点','自然风光','景点','美食','自然','历史'], prefs: { algorithm: 'content_based', sort_by: 'score', top_n: 100, categories: [] } },
			// 路径搜索
			routeSearch: { query: '', loading: false, results: [], error: null }
		}
	},
	computed: {
		markers() {
			if (this.activeTab === 'place') {
				return (this.place.list || []).filter(p => typeof p.latitude==='number' && typeof p.longitude==='number')
					.map(p => ({ id: p.id ?? p.attraction_id ?? p.name, name: p.name, latitude: p.latitude, longitude: p.longitude, popup: p.name }))
			}
			if (this.activeTab === 'recommend') {
				return (this.recommend.list || []).filter(r => typeof r.latitude==='number' && typeof r.longitude==='number')
					.map(r => ({ id: this.getId(r), name: r.name, latitude: r.latitude, longitude: r.longitude, popup: r.name }))
			}
			if (this.activeTab === 'route') {
				return (this.routeMarkers || []).filter(p => typeof p.latitude==='number' && typeof p.longitude==='number')
					.map((p, idx) => ({
						id: `route-${idx + 1}`,
						name: p.label || `路线点 ${idx + 1}`,
						latitude: p.latitude,
						longitude: p.longitude,
						popup: `${p.label || '路线点'} · ${p.latitude.toFixed(4)}, ${p.longitude.toFixed(4)}`
					}))
			}
			return []
		},
		routeStats() {
			const points = this.routeMarkers.length
			const segments = Math.max(points - 1, 0)
			const rawDistance = this.routeInfo?.distance_km
			const distanceValue = typeof rawDistance === 'number' ? rawDistance : parseFloat(rawDistance)
			const distanceLabel = Number.isFinite(distanceValue) && distanceValue > 0 ? distanceValue.toFixed(1) : '--'
			const distanceText = distanceLabel === '--' ? '--' : `${distanceLabel} km`
			return { points, segments, distanceValue, distanceLabel, distanceText }
		},
		// 预计时间（假设平均速度40km/h）
		estimatedTime() {
			const distance = this.routeStats.distanceValue
			if (!Number.isFinite(distance) || distance <= 0) return '--'
			const hours = distance / 40
			if (hours < 1) {
				return `${Math.round(hours * 60)}分钟`
			} else {
				const h = Math.floor(hours)
				const m = Math.round((hours - h) * 60)
				return m > 0 ? `${h}小时${m}分钟` : `${h}小时`
			}
		},
		roadPathCoords() {
			// 从 routeInfo 中提取道路路径坐标
			if (!this.routeInfo) return []
			// 尝试从不同位置获取路径数据
			const path = this.routeInfo.data?.road_path || this.routeInfo.road_path || []
			return Array.isArray(path) ? path : []
		}
	},
	async mounted() {
		// 初始化类别、附近与推荐
		this.place.categories = await fetchCategories()
			// 初始将输入与中心同步
			this.place.lat = this.mapCenter[0]; this.place.lon = this.mapCenter[1]
			await Promise.all([this.loadNearby(), this.refreshRecommend()])
		
		// 监听来自AI助手的路线导入事件
		window.addEventListener('import-ai-route', this.handleImportAIRoute);
	},
	beforeUnmount() {
		// 清理事件监听
		window.removeEventListener('import-ai-route', this.handleImportAIRoute);
	},
	methods: {
		goLogin() {
			try { this.$router.push('/login') } catch (e) {}
		},
		switchTab(tab) { this.activeTab = tab },
		locate() { this.$refs.baseMap?.locateUser?.(false) },
		onLocationUpdate(pos) {
			if (!pos) return
			// 更新默认地图中心
			this.mapCenter = [pos.latitude, pos.longitude]
				// 同步到"附近"输入
				this.place.lat = pos.latitude
				this.place.lon = pos.longitude
		},
		onMarkerClick(item) {
			if (!item) return
			this.selectedId = item.id
		},
		// --- 附近 ---
			async loadNearby() {
			this.place.loading = true
			try {
					const lat = this.place.lat ?? this.mapCenter[0]
					const lon = this.place.lon ?? this.mapCenter[1]
					const list = await fetchNearbyPlaces({ lat, lon, radius: this.place.radius, category: this.place.category || undefined, limit: 200 })
				this.place.list = list
				if (list.length) this.selectedId = list[0].id || list[0].attraction_id
			} catch (e) {
				console.error('加载附近失败', e)
				this.place.list = []
			} finally { this.place.loading = false }
		},
		focusPlace(p) {
			this.selectedId = p.id || p.attraction_id
			if (typeof p.latitude==='number' && typeof p.longitude==='number') this.mapCenter = [p.latitude, p.longitude]
		},
			syncMapCenter() {
				this.place.lat = this.mapCenter[0]
				this.place.lon = this.mapCenter[1]
			},
		// --- 推荐 ---
		getId(it) { return it.attraction_id || it.id || it.name },
		async refreshRecommend() {
			this.recommend.loading = true
			try {
				let list = []
				if (this.recommend.query && this.recommend.query.trim()) {
					list = await searchRecommendations({ query: this.recommend.query, limit: this.recommend.prefs.top_n || 100 })
				} else {
					list = await fetchRecommendations({ user_id: 1, top_n: this.recommend.prefs.top_n || 100, algorithm: this.recommend.prefs.algorithm })
					if (this.recommend.prefs.sort_by && this.recommend.prefs.sort_by !== 'score') {
						const key = this.recommend.prefs.sort_by
						list = [...list].sort((a, b) => (b[key] || 0) - (a[key] || 0))
					}
				}
				if (this.recommend.prefs.categories?.length) {
					list = list.filter(d => this.recommend.prefs.categories.includes(d.type) || this.recommend.prefs.categories.includes(d.category))
				}
				this.recommend.list = list
				const first = list.find(it => typeof it.latitude==='number' && typeof it.longitude==='number')
				if (first) { this.selectedId = this.getId(first); this.mapCenter = [first.latitude, first.longitude] }
			} catch (e) {
				console.error('加载推荐失败', e)
				this.recommend.list = []
			} finally { this.recommend.loading = false }
		},
		focusRecommend(r) {
			this.selectedId = this.getId(r)
			if (typeof r.latitude==='number' && typeof r.longitude==='number') this.mapCenter = [r.latitude, r.longitude]
		},
		// --- 路径 ---
		toggleRouteMode() { this.routeMode = !this.routeMode },
		undoRoute() { if (this.routeMarkers.length) this.routeMarkers.pop() },
		clearRoute() { this.routeMarkers = []; this.routeInfo = null },
		reverseRoute() { if (this.routeMarkers.length>=2) this.routeMarkers = [...this.routeMarkers].reverse() },
		// 计算两点之间的距离（Haversine公式）
		calculateDistance(lat1, lon1, lat2, lon2) {
			const R = 6371 // 地球半径（公里）
			const dLat = (lat2 - lat1) * Math.PI / 180
			const dLon = (lon2 - lon1) * Math.PI / 180
			const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
				Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
				Math.sin(dLon / 2) * Math.sin(dLon / 2)
			const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
			return R * c
		},
		// 使用贪心算法（最近邻）获取优化后的路线顺序
		getOptimizedRoute(markers) {
			if (markers.length < 3) return markers
			
			// 固定第一个点作为起点
			const start = markers[0]
			const remaining = [...markers.slice(1)]
			const optimized = [start]
			
			// 贪心算法：每次选择距离当前点最近的未访问点
			while (remaining.length > 0) {
				const current = optimized[optimized.length - 1]
				let nearestIndex = 0
				let minDistance = this.calculateDistance(
					current.latitude, current.longitude,
					remaining[0].latitude, remaining[0].longitude
				)
				
				for (let i = 1; i < remaining.length; i++) {
					const dist = this.calculateDistance(
						current.latitude, current.longitude,
						remaining[i].latitude, remaining[i].longitude
					)
					if (dist < minDistance) {
						minDistance = dist
						nearestIndex = i
					}
				}
				
				optimized.push(remaining[nearestIndex])
				remaining.splice(nearestIndex, 1)
			}
			
			return optimized
		},
		async planSimpleRoute() {
			if (this.routeMarkers.length < 2) return
			this.planning = true
			try {
				// 根据模式决定是否优化顺序
				let markers = [...this.routeMarkers]
				
				if (this.optimizeMode && markers.length >= 3) {
					// 智能优化模式：自动优化访问顺序
					markers = this.getOptimizedRoute(markers)
				}
				// 否则使用原始顺序（顺序模式）
				
				// 提取起点和终点
				const start = markers[0]
				const end = markers[markers.length - 1]
				
				// 提取中间waypoints（如果有的话）
				const waypoints = markers.slice(1, -1)
				
				// 调用多点路径规划API
				const info = await planSimple(start, end, waypoints)
				this.routeInfo = info
				
				// 路线计算成功后显示结果弹窗
				if (info) {
					this.showRouteResult = true
				}
			} catch (e) { 
				console.error('路线计算失败', e)
				this.routeInfo = null 
			} finally { 
				this.planning = false 
			}
		},
		// 获取两个站点之间的距离
		getSegmentDistance(index) {
			if (index >= this.routeMarkers.length - 1) return 0
			const p1 = this.routeMarkers[index]
			const p2 = this.routeMarkers[index + 1]
			return this.calculateDistance(p1.latitude, p1.longitude, p2.latitude, p2.longitude)
		},
		// 获取段落预计时间
		getSegmentTime(index) {
			const distance = this.getSegmentDistance(index)
			if (distance === 0) return '--'
			const hours = distance / 40 // 假设平均速度40km/h
			const minutes = Math.round(hours * 60)
			if (minutes < 60) {
				return `${minutes}分钟`
			} else {
				const h = Math.floor(minutes / 60)
				const m = minutes % 60
				return m > 0 ? `${h}小时${m}分钟` : `${h}小时`
			}
		},
		// 导出路线
		exportRoute() {
			if (this.routeMarkers.length < 2) return
			
			// 构建导出数据
			const data = {
				title: '旅行路线',
				created_at: new Date().toISOString(),
				total_distance: this.routeStats.distanceLabel + ' km',
				estimated_time: this.estimatedTime,
				points: this.routeMarkers.map((p, i) => ({
					sequence: i + 1,
					name: p.label || `站点 ${i + 1}`,
					latitude: p.latitude,
					longitude: p.longitude,
					source: p.source,
					distance_to_next: i < this.routeMarkers.length - 1 ? this.getSegmentDistance(i).toFixed(2) + ' km' : null
				}))
			}
			
			// 转换为JSON字符串
			const json = JSON.stringify(data, null, 2)
			
			// 创建下载链接
			const blob = new Blob([json], { type: 'application/json' })
			const url = URL.createObjectURL(blob)
			const a = document.createElement('a')
			a.href = url
			a.download = `旅行路线_${new Date().getTime()}.json`
			document.body.appendChild(a)
			a.click()
			document.body.removeChild(a)
			URL.revokeObjectURL(url)
			
			// 提示用户
			alert('路线已导出!')
		},
		// 来自 BaseMap 的事件
		// route-point-add
		onRoutePointAdd(p) { this.addRouteMarker(p) },
		onMapClick(pos) {
			if (this.activeTab !== 'route' || !this.routeMode || !pos) return
			this.addRouteMarker({
				latitude: pos.latitude,
				longitude: pos.longitude,
				label: `自选点 ${this.routeMarkers.length + 1}`,
				source: 'map'
			})
		},
		addRoutePointFromSearch(place) {
			if (!place || typeof place.latitude !== 'number' || typeof place.longitude !== 'number') return
			this.addRouteMarker({
				latitude: place.latitude,
				longitude: place.longitude,
				label: place.title,
				source: 'search',
				meta: { subtitle: place.subtitle }
			})
		},
		focusRouteCandidate(place) {
			if (!place || typeof place.latitude !== 'number' || typeof place.longitude !== 'number') return
			this.mapCenter = [place.latitude, place.longitude]
		},
		addRouteMarker(point) {
			if (!point || typeof point.latitude !== 'number' || typeof point.longitude !== 'number') return
			const label = point.label?.trim() || `路线点 ${this.routeMarkers.length + 1}`
			const marker = {
				latitude: point.latitude,
				longitude: point.longitude,
				label,
				source: point.source || 'map',
				meta: point.meta || null
			}
			this.routeMarkers = [...this.routeMarkers, marker]
			this.mapCenter = [marker.latitude, marker.longitude]
		},
		async searchRoutePlaces() {
			const keyword = (this.routeSearch.query || '').trim()
			if (!keyword) {
				this.routeSearch.results = []
				this.routeSearch.error = null
				return
			}
			this.routeSearch.loading = true
			this.routeSearch.error = null
			try {
				const results = await searchPlaces(keyword, { limit: 8 })
				this.routeSearch.results = results
			} catch (e) {
				this.routeSearch.results = []
				this.routeSearch.error = '地点搜索失败，请稍后重试。'
			} finally {
				this.routeSearch.loading = false
			}
		},
		/**
		 * 处理从AI助手导入路线的请求
		 */
		async handleImportAIRoute(event) {
			const { attractions } = event.detail;
			
			if (!attractions || attractions.length === 0) {
				alert('没有可导入的景点');
				return;
			}
			
			console.log('[Home] 开始导入AI推荐的景点:', attractions);
			
			// 显示加载状态
			this.planning = true;
			
			try {
				// 动态导入API方法
				const { searchAttractions } = await import('@/api/place');
				
				// 批量查询景点坐标
				const results = await searchAttractions(attractions);
				
				console.log('[Home] 查询到的景点信息:', results);
				
				if (results.length === 0) {
					alert('未能找到任何景点的坐标信息，请尝试更具体的景点名称');
					return;
				}
				
				// 清空现有路线
				this.routeMarkers = [];
				
				// 将查询到的景点添加到路线
				for (const attraction of results) {
					this.routeMarkers.push({
						latitude: attraction.latitude,
						longitude: attraction.longitude,
						label: attraction.name,
						source: 'ai',
						meta: {
							subtitle: attraction.description || attraction.category,
							category: attraction.category
						}
					});
				}
				
			// 切换到路径规划标签
			this.activeTab = 'route';
			
			// 定位到第一个景点
			if (results.length > 0) {
				this.mapCenter = [results[0].latitude, results[0].longitude];
			}
			
			// 等待UI更新后计算路线
			await this.$nextTick();
			
			// 自动计算路线
			if (this.routeMarkers.length >= 2) {
				await this.planSimpleRoute();
				
				// 显示成功消息
				const missed = attractions.length - results.length;
				const msg = missed > 0 
					? `✅ 成功导入 ${results.length} 个景点并规划路线！\n⚠️ ${missed} 个景点未找到坐标`
					: `✅ 成功导入 ${results.length} 个景点并规划路线！`;
				alert(msg);
			} else if (results.length === 1) {
				alert(`✅ 导入了 1 个景点，至少需要 2 个景点才能规划路线`);
			}
			
			console.log(`[Home] 导入完成: ${results.length}/${attractions.length} 个景点`);
				
			} catch (error) {
				console.error('[Home] 导入AI路线失败:', error);
				alert('导入失败：' + error.message);
			} finally {
				this.planning = false;
			}
		}
	}
}
</script>

<style scoped>
@keyframes slideUp {
	from {
		opacity: 0;
		transform: translateY(20px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

/* 加载动画 */
@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}

.animate-spin {
	animation: spin 1s linear infinite;
}

/* 自定义滚动条 */
.overflow-y-auto::-webkit-scrollbar {
	width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
	background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
	background: #cbd5e1;
	border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
	background: #94a3b8;
}
</style>
