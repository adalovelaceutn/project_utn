import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { KolbProfile, KolbProfilePayload, ProfileTheory } from './models';

export type KolbProfileUpdatePayload = Partial<Omit<KolbProfilePayload, 'user_id'>>;

@Injectable({ providedIn: 'root' })
export class KolbService {
  constructor(private readonly http: HttpClient) {}

  getByUser(userId: string): Observable<KolbProfile> {
    return this.http.get<KolbProfile>(`${environment.apiBaseUrl}/kolb-profiles/by-user/${userId}`);
  }

  getByUserOptional(userId: string): Observable<KolbProfile | null> {
    return this.http.get<KolbProfile | null>(`${environment.apiBaseUrl}/kolb-profiles/by-user/${userId}/optional`);
  }

  getByUsernameOptional(username: string): Observable<KolbProfile | null> {
    return this.http.get<KolbProfile | null>(`${environment.apiBaseUrl}/kolb-profiles/by-username/${username}/optional`);
  }

  create(payload: KolbProfilePayload): Observable<KolbProfile> {
    return this.http.post<KolbProfile>(`${environment.apiBaseUrl}/kolb-profiles`, payload);
  }

  update(profileId: string, payload: KolbProfileUpdatePayload): Observable<KolbProfile> {
    return this.http.patch<KolbProfile>(`${environment.apiBaseUrl}/kolb-profiles/${profileId}`, payload);
  }

  delete(profileId: string): Observable<void> {
    return this.http.delete<void>(`${environment.apiBaseUrl}/kolb-profiles/${profileId}`);
  }
  
    getTheory(style: string): Observable<ProfileTheory> {
      return this.http.get<ProfileTheory>(`/main-api/theory/${encodeURIComponent(style)}`);
    }
}