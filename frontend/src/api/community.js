import api from './index'

// 获取公开日记列表
export async function fetchPublicDiaries(page = 1, limit = 20) {
  try {
    const { data } = await api.get('/api/community/diaries', { params: { page, limit } })
    if (data?.success) {
      return {
        diaries: data.diaries || [],
        pagination: data.pagination || { page, limit, total: 0 }
      }
    }
    return { diaries: [], pagination: { page, limit, total: 0 } }
  } catch (error) {
    console.error('获取公开日记失败:', error)
    return { diaries: [], pagination: { page, limit, total: 0 } }
  }
}

// 获取日记详情
export async function fetchDiaryDetail(diaryId) {
  try {
    const { data } = await api.get(`/api/community/diaries/${diaryId}`)
    if (data?.success) {
      return data.diary
    }
    throw new Error(data?.message || '获取日记详情失败')
  } catch (error) {
    console.error('获取日记详情失败:', error)
    throw error
  }
}

// 点赞/取消点赞
export async function toggleLike(diaryId) {
  try {
    const { data } = await api.post(`/api/community/diaries/${diaryId}/like`)
    if (data?.success) {
      return {
        action: data.action, // 'liked' or 'unliked'
        likeCount: data.like_count
      }
    }
    throw new Error(data?.message || '点赞操作失败')
  } catch (error) {
    console.error('点赞操作失败:', error)
    throw error
  }
}

// 获取评论列表
export async function fetchComments(diaryId) {
  try {
    const { data } = await api.get(`/api/community/diaries/${diaryId}/comments`)
    if (data?.success) {
      return data.comments || []
    }
    return []
  } catch (error) {
    console.error('获取评论失败:', error)
    return []
  }
}

// 添加评论
export async function addComment(diaryId, content, parentId = null) {
  try {
    const { data } = await api.post(`/api/community/diaries/${diaryId}/comments`, {
      content,
      parent_id: parentId
    })
    if (data?.success) {
      return data.comment
    }
    throw new Error(data?.message || '添加评论失败')
  } catch (error) {
    console.error('添加评论失败:', error)
    throw error
  }
}

// 关注/取消关注用户
export async function toggleFollow(userId) {
  try {
    const { data } = await api.post(`/api/community/users/${userId}/follow`)
    if (data?.success) {
      return data.action // 'followed' or 'unfollowed'
    }
    throw new Error(data?.message || '关注操作失败')
  } catch (error) {
    console.error('关注操作失败:', error)
    throw error
  }
}
