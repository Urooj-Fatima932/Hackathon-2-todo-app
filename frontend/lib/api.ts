import {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskListResponse,
  ApiError,
  TaskFilter,
  ChatRequest,
  ChatResponse,
  ConversationListResponse,
  ConversationDetailResponse,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "auth_token";

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private getAuthToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit,
    requiresAuth: boolean = true
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options?.headers as Record<string, string>),
    };

    // Add auth header if token exists and endpoint requires auth
    if (requiresAuth) {
      const token = this.getAuthToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle 204 No Content
      if (response.status === 204) {
        return undefined as T;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          error: "Unknown Error",
          message: `HTTP Error ${response.status}`,
          statusCode: response.status,
        }));

        // Handle 401 Unauthorized - clear token and redirect
        if (response.status === 401) {
          if (typeof window !== "undefined") {
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem("auth_user");
            window.location.href = "/login";
          }
        }

        throw {
          ...errorData,
          statusCode: response.status,
        } as ApiError;
      }

      return response.json();
    } catch (error) {
      if ((error as ApiError).statusCode) {
        throw error;
      }

      // Network or other errors
      throw {
        error: "NetworkError",
        message:
          error instanceof Error ? error.message : "Failed to fetch data",
        statusCode: 0,
      } as ApiError;
    }
  }

  async get<T>(endpoint: string, requiresAuth: boolean = true): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" }, requiresAuth);
  }

  async post<T>(endpoint: string, data?: unknown, requiresAuth: boolean = true): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: "POST",
        body: data ? JSON.stringify(data) : undefined,
      },
      requiresAuth
    );
  }

  async patch<T>(endpoint: string, data?: unknown, requiresAuth: boolean = true): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: "PATCH",
        body: data ? JSON.stringify(data) : undefined,
      },
      requiresAuth
    );
  }

  async delete<T>(endpoint: string, requiresAuth: boolean = true): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" }, requiresAuth);
  }

  // Task-specific methods (all require auth)

  async getTasks(filter: TaskFilter = "all"): Promise<Task[]> {
    const endpoint =
      filter === "all" ? "/api/tasks" : `/api/tasks?status=${filter}`;
    const response = await this.get<TaskListResponse>(endpoint);
    return response.tasks;
  }

  async getTask(id: string): Promise<Task> {
    return this.get<Task>(`/api/tasks/${id}`);
  }

  async createTask(data: CreateTaskRequest): Promise<Task> {
    return this.post<Task>("/api/tasks", data);
  }

  async updateTask(id: string, data: UpdateTaskRequest): Promise<Task> {
    return this.patch<Task>(`/api/tasks/${id}`, data);
  }

  async toggleTask(id: string): Promise<Task> {
    return this.post<Task>(`/api/tasks/${id}/toggle`);
  }

  async deleteTask(id: string): Promise<void> {
    return this.delete<void>(`/api/tasks/${id}`);
  }

  // Chat-specific methods (all require auth)

  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    const request: ChatRequest = { message };
    if (conversationId) {
      request.conversation_id = conversationId;
    }
    return this.post<ChatResponse>("/api/chat", request);
  }

  async getConversations(): Promise<ConversationListResponse> {
    return this.get<ConversationListResponse>("/api/conversations");
  }

  async getConversation(id: string): Promise<ConversationDetailResponse> {
    return this.get<ConversationDetailResponse>(`/api/conversations/${id}`);
  }

  async deleteConversation(id: string): Promise<void> {
    return this.delete<void>(`/api/conversations/${id}`);
  }
}

export const api = new ApiClient(API_BASE_URL);
