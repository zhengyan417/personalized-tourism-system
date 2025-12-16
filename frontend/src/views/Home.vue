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
			</div>

			<!-- 内容区域 -->
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
							<p class="text-xs text-white/80">提示：点击地图即可添加站点，建议不少于两个坐标点以获取完整线路。</p>
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

				<!-- 日记 -->
				<div v-else-if="activeTab==='diary'" class="space-y-4">
					<div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 space-y-3">
						<div>
							<label class="block text-xs font-medium text-gray-500 mb-1">标题</label>
							<input v-model.trim="diary.form.title" type="text" class="w-full rounded-lg border-gray-200 text-sm focus:ring-brand-500 focus:border-brand-500" placeholder="给日记起个标题..." />
						</div>
						<div>
							<label class="block text-xs font-medium text-gray-500 mb-1">内容</label>
							<textarea v-model.trim="diary.form.content" rows="3" class="w-full rounded-lg border-gray-200 text-sm focus:ring-brand-500 focus:border-brand-500 resize-none" placeholder="记录此刻的心情与见闻..."></textarea>
						</div>
						<div class="grid grid-cols-2 gap-3">
							<div>
								<label class="block text-xs font-medium text-gray-500 mb-1">纬度</label>
								<input v-model.number="diary.form.latitude" type="number" step="0.000001" class="w-full rounded-lg border-gray-200 text-xs bg-gray-50" readonly />
							</div>
							<div>
								<label class="block text-xs font-medium text-gray-500 mb-1">经度</label>
								<input v-model.number="diary.form.longitude" type="number" step="0.000001" class="w-full rounded-lg border-gray-200 text-xs bg-gray-50" readonly />
							</div>
						</div>
						<div class="flex gap-2 pt-1">
							<button class="px-3 py-1.5 border border-gray-200 rounded-lg text-xs text-gray-600 hover:bg-gray-50" @click="locate">
								<i class="bi bi-geo-alt"></i> 获取位置
							</button>
							<button class="flex-1 bg-brand-600 text-white py-1.5 rounded-lg text-xs font-medium hover:bg-brand-700 transition-colors flex items-center justify-center gap-2" :disabled="diary.submitting" @click="submitDiary">
								<span v-if="diary.submitting" class="spinner-border spinner-border-sm w-3 h-3"></span>
								<i class="bi bi-send"></i> 发布日记
							</button>
						</div>
					</div>

					<div class="space-y-2">
						<div v-if="diary.list.length===0" class="text-center py-8 text-gray-400">
							<i class="bi bi-journal-album text-4xl mb-2 block"></i>
							<p class="text-sm">暂无日记，开始记录吧！</p>
						</div>
						<button v-for="d in diary.list" :key="d.id" 
							class="w-full text-left bg-white p-3 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group"
							:class="{ 'ring-2 ring-brand-500 border-transparent': selectedId === d.id }"
							@click="selectDiary(d)">
							<div class="flex justify-between items-start mb-1">
								<h4 class="font-bold text-gray-800 group-hover:text-brand-600 transition-colors line-clamp-1">{{ d.title }}</h4>
								<span class="text-[10px] text-gray-400 whitespace-nowrap">{{ d.date }}</span>
							</div>
							<p class="text-xs text-gray-500 line-clamp-2">{{ d.snippet || d.content }}</p>
						</button>
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
	</div>
</template>

<script>
import BaseMap from '../components/map/BaseMap.vue'
import { fetchNearbyPlaces, fetchCategories } from '../api/place'
import { fetchRecommendations, searchRecommendations } from '../api/recommendation'
import { planSimple } from '../api/route'
import { fetchDiaries, fetchDiaryDetail, createDiary } from '../api/diary'
import { searchPlaces } from '../api/geocode'

export default {
	name: 'Home',
	components: { BaseMap },
	data() {
		return {
			tabs: [
				{ id: 'place', name: '附近', icon: 'bi-geo-alt' },
				{ id: 'recommend', name: '推荐', icon: 'bi-stars' },
				{ id: 'route', name: '路径', icon: 'bi-sign-turn-right' },
				{ id: 'diary', name: '日记', icon: 'bi-journal-text' }
			],
			activeTab: 'place',
			mapCenter: [39.9042, 116.4074],
			selectedId: null,
			// 路径
			routeMode: false,
			routeMarkers: [],
			routeInfo: null,
			planning: false,
			// 附近
			place: { lat: 39.9042, lon: 116.4074, radius: 5, category: '', categories: [], list: [], loading: false },
			// 推荐
			recommend: { query: '', list: [], loading: false, showAdv: false, categories: ['历史景点','自然风光','景点','美食','自然','历史'], prefs: { algorithm: 'content_based', sort_by: 'score', top_n: 100, categories: [] } },
			// 日记
			diary: { list: [], selected: null, submitting: false, form: { title: '', content: '', latitude: null, longitude: null } },
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
			if (this.activeTab === 'diary') {
				return (this.diary.list || []).filter(d => typeof d.latitude==='number' && typeof d.longitude==='number')
					.map(d => ({ id: d.id, name: d.title, latitude: d.latitude, longitude: d.longitude, popup: `${d.title} · ${d.date||''}` }))
			}
			return []
		}
	,
		routeStats() {
			const points = this.routeMarkers.length
			const segments = Math.max(points - 1, 0)
			const rawDistance = this.routeInfo?.distance_km
			const distanceValue = typeof rawDistance === 'number' ? rawDistance : parseFloat(rawDistance)
			const distanceLabel = Number.isFinite(distanceValue) && distanceValue > 0 ? distanceValue.toFixed(1) : '--'
			const distanceText = distanceLabel === '--' ? '--' : `${distanceLabel} km`
			return { points, segments, distanceValue, distanceLabel, distanceText }
		}
	},
	async mounted() {
		// 初始化类别、附近与推荐、日记
		this.place.categories = await fetchCategories()
			// 初始将输入与中心同步
			this.place.lat = this.mapCenter[0]; this.place.lon = this.mapCenter[1]
			await Promise.all([this.loadNearby(), this.refreshRecommend(), this.loadDiaries()])
	},
	methods: {
		goLogin() {
			try { this.$router.push('/login') } catch (e) {}
		},
		switchTab(tab) { this.activeTab = tab },
		locate() { this.$refs.baseMap?.locateUser?.(false) },
		onLocationUpdate(pos) {
			if (!pos) return
			// 更新默认地图中心与日记坐标
			this.mapCenter = [pos.latitude, pos.longitude]
				// 同步到“附近”输入
				this.place.lat = pos.latitude
				this.place.lon = pos.longitude
			if (this.activeTab === 'diary') {
				this.diary.form.latitude = pos.latitude
				this.diary.form.longitude = pos.longitude
			}
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
		async planSimpleRoute() {
			if (this.routeMarkers.length < 2) return
			this.planning = true
			try {
				const info = await planSimple(this.routeMarkers[0], this.routeMarkers[this.routeMarkers.length - 1])
				this.routeInfo = info
			} catch (e) { console.error('路线计算失败', e); this.routeInfo = null } finally { this.planning = false }
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
		// --- 日记 ---
		async loadDiaries() {
			try {
				const list = await fetchDiaries({ user_id: 1 })
				this.diary.list = Array.isArray(list) ? list : []
			} catch (e) { console.error('加载日记失败', e); this.diary.list = [] }
		},
		async submitDiary() {
			if (!this.diary.form.title || !this.diary.form.content) return
			this.diary.submitting = true
			try {
				const created = await createDiary({
					user_id: 1,
					title: this.diary.form.title,
					content: this.diary.form.content,
					latitude: this.diary.form.latitude,
					longitude: this.diary.form.longitude
				})
				if (created) {
					this.diary.list = [created, ...this.diary.list]
					this.activeTab = 'diary'
					this.selectedId = created.id
					if (typeof created.latitude==='number' && typeof created.longitude==='number') this.mapCenter = [created.latitude, created.longitude]
					this.diary.form = { title: '', content: '', latitude: null, longitude: null }
				}
			} catch (e) { console.error('创建日记失败', e) } finally { this.diary.submitting = false }
		},
		async selectDiary(d) {
			try {
				const detail = await fetchDiaryDetail(d.id)
				this.diary.selected = detail || d
			} catch { this.diary.selected = d }
			this.selectedId = d.id
			if (typeof d.latitude==='number' && typeof d.longitude==='number') this.mapCenter = [d.latitude, d.longitude]
		}
	}
}
</script>
