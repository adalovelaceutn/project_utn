import { Injectable, computed, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

import { environment } from '../../environments/environment';
import { AuthResponse, UserCreate, UserLogin, UserPublic } from './models';

const TOKEN_KEY = 'kolb_token';
const USER_KEY = 'kolb_user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly userSignal = signal<UserPublic | null>(this.loadUser());

  constructor(private readonly http: HttpClient) {}

  readonly currentUser = computed(() => this.userSignal());
  readonly isAuthenticated = computed(() => !!this.userSignal() && !!this.getToken());

  register(payload: UserCreate): Observable<UserPublic> {
    return this.http.post<UserPublic>(`${environment.apiBaseUrl}/users`, payload);
  }

  login(payload: UserLogin): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${environment.apiBaseUrl}/auth/login`, payload).pipe(
      tap((response) => {
        localStorage.setItem(TOKEN_KEY, response.access_token);
        localStorage.setItem(USER_KEY, JSON.stringify(response.user));
        this.userSignal.set(response.user);
      })
    );
  }

  setCurrentUser(user: UserPublic): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    this.userSignal.set(user);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.userSignal.set(null);
  }

  private loadUser(): UserPublic | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw) as UserPublic;
    } catch {
      localStorage.removeItem(USER_KEY);
      return null;
    }
  }
}