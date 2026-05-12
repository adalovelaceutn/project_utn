import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { UserCreate, UserPublic } from './models';

export interface UserUpdatePayload {
  dni?: string;
  nombre?: string;
  apellido?: string;
  email?: string;
  telefono?: string;
  password?: string;
}

@Injectable({ providedIn: 'root' })
export class UserService {
  constructor(private readonly http: HttpClient) {}

  list(): Observable<UserPublic[]> {
    return this.http.get<UserPublic[]>(`${environment.apiBaseUrl}/users`);
  }

  getById(userId: string): Observable<UserPublic> {
    return this.http.get<UserPublic>(`${environment.apiBaseUrl}/users/${userId}`);
  }

  create(payload: UserCreate): Observable<UserPublic> {
    return this.http.post<UserPublic>(`${environment.apiBaseUrl}/users`, payload);
  }

  update(userId: string, payload: UserUpdatePayload): Observable<UserPublic> {
    return this.http.patch<UserPublic>(`${environment.apiBaseUrl}/users/${userId}`, payload);
  }

  delete(userId: string): Observable<void> {
    return this.http.delete<void>(`${environment.apiBaseUrl}/users/${userId}`);
  }
}