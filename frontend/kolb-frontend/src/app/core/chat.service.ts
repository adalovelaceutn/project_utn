import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { AuthService } from './auth.service';
import { ChatResponse } from './models';

@Injectable({ providedIn: 'root' })
export class ChatService {
  constructor(
    private readonly http: HttpClient,
    private readonly authService: AuthService
  ) {}

  sendMessage(message: string, sessionId: string | null): Observable<ChatResponse> {
    const user = this.authService.currentUser();
    if (!user) {
      throw new Error('No hay un usuario autenticado para iniciar la entrevista.');
    }

    return this.http.post<ChatResponse>('/main-api/chat', {
      message,
      session_id: sessionId,
      user: {
        id: user.id,
        username: user.username,
        nombre: user.nombre,
        apellido: user.apellido,
        email: user.email,
        dni: user.dni,
      }
    });
  }
}