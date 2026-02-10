// Core Entities

export interface User {
  id: string;
  email: string;
  name?: string | null;
  created_at: string;
}

// Auth Types

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

// API Request/Response Types

export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page?: number;
  pageSize?: number;
}

export interface ApiError {
  error: string;
  message: string;
  details?: unknown;
  statusCode: number;
}

// Derived Types

export type TaskFilter = "all" | "pending" | "completed";

export interface TaskFormData {
  title: string;
  description: string;
}

// Client-Side State Types

export interface OptimisticTask extends Task {
  pending?: boolean;
  error?: string;
}

export interface UIState {
  isCreateDialogOpen: boolean;
  editingTaskId: string | null;
  isLoading: boolean;
  error: string | null;
}

// Chat Types

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  tool_calls: ToolCall[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  tool_calls?: ToolCall[];
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
}

export interface ConversationDetailResponse {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}
