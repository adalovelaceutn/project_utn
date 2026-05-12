export interface UserPublic {
  id: string;
  username: string;
  dni: string;
  nombre: string;
  apellido: string;
  email: string;
  telefono: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  password: string;
  dni: string;
  nombre: string;
  apellido: string;
  email: string;
  telefono: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserPublic;
}

export interface KolbDimensions {
  experiencia_concreta: number;
  observacion_reflexiva: number;
  conceptualizacion_abstracta: number;
  experimentacion_activa: number;
}

export interface KolbProfile {
  id: string;
  dni: string;
  puntajes: KolbDimensions;
  confidence_score?: number | null;
  interview_responses?: Array<{
    scenario: string;
    response: string;
    classification: string;
  }> | null;
  created_at: string;
  updated_at: string;
}

export interface KolbProfilePayload {
  dni: string;
  puntajes: KolbDimensions;
  confidence_score?: number | null;
  interview_responses?: Array<{
    scenario: string;
    response: string;
    classification: string;
  }> | null;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
  timestamp: Date;
}

export interface ChatResponse {
  session_id: string;
  task_id: string;
  state: string;
  reply: string;
  profile: Record<string, unknown> | null;
  persisted_profile_id: string | null;
}

export interface ProfileTheory {
  nombre: string;
  formula: string;
  descripcion: string;
  estrategia_agente: string;
  ejes: Record<string, string>;
  descripcion_modelo: string;
}