import { request } from '../utils/request.js'

/**
 * 抽牌：POST /api/draw
 * @returns {Promise<{ card_name, base_meaning, narrative, artwork, card_image_url }>}
 */
export function drawCard() {
  return request({ url: '/api/draw', method: 'POST', data: {} })
}
