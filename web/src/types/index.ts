export interface Car {
  uuid: string
  plate_number: string
  make: string
  model: string
  variant: string
  colour: string
  nickname: string
  created_at: string
}

export interface PublicCar {
  uuid: string
  nickname: string
  make: string
  model: string
}

export interface ChatThread {
  uuid: string
  car_nickname: string
  car_make: string
  car_model: string
  created_at: string
  is_active: boolean
  last_message: { content: string; timestamp: string } | null
}

export interface Message {
  uuid: string
  sender_label: string
  content: string
  timestamp: string
  is_read: boolean
  is_system: boolean
}

export interface CallToken {
  channel_id: string
  token: string
  app_id: string
}
