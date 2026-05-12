import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { catchError, finalize, of, tap, timeout } from 'rxjs';

import { AuthService } from '../../core/auth.service';
import { KolbService } from '../../core/kolb.service';
import { KolbProfile, ProfileTheory } from '../../core/models';

@Component({
  selector: 'app-kolb-profile',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule
  ],
  templateUrl: './kolb-profile.component.html',
  styleUrl: './kolb-profile.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class KolbProfileComponent implements OnInit {
  profile: KolbProfile | null = null;
  loading = false;

  theory: ProfileTheory | null = null;
  theoryLoading = false;

  readonly kolbTheory = [
    'Experiencia Concreta: aprendes haciendo y conectando con situaciones reales.',
    'Observacion Reflexiva: aprendes analizando lo ocurrido y escuchando otras perspectivas.',
    'Conceptualizacion Abstracta: aprendes estructurando modelos, ideas y conceptos.',
    'Experimentacion Activa: aprendes probando soluciones y aplicando cambios.'
  ];

  constructor(
    private readonly authService: AuthService,
    private readonly kolbService: KolbService,
    private readonly cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  private loadProfile(): void {
    const user = this.authService.currentUser();
    if (!user) {
      return;
    }

    this.loading = true;
    this.cdr.markForCheck();

    this.kolbService
      .getByUsernameOptional(user.username)
      .pipe(
        tap((profile) => {
          console.log('[KolbProfile] API response:', profile);
          this.profile = profile;
          if (profile?.predominant_style) {
            this.loadTheory(profile.predominant_style);
          }
          this.cdr.markForCheck();
        }),
        timeout(8000),
        catchError((err) => {
          console.error('[KolbProfile] Error loading profile:', err);
          return of(null);
        }),
        finalize(() => {
          console.log('[KolbProfile] Loading complete');
          this.loading = false;
          this.cdr.markForCheck();
        })
      )
      .subscribe();
  }

  private loadTheory(style: string): void {
    this.theoryLoading = true;
    this.cdr.markForCheck();

    this.kolbService
      .getTheory(style)
      .pipe(
        tap((theory) => {
          console.log('[KolbProfile] Theory loaded:', theory);
          this.theory = theory;
          this.cdr.markForCheck();
        }),
        timeout(5000),
        catchError((err) => {
          console.error('[KolbProfile] Error loading theory:', err);
          return of(null);
        }),
        finalize(() => {
          this.theoryLoading = false;
          this.cdr.markForCheck();
        })
      )
      .subscribe();
  }

  get radarPoints(): string {
    if (!this.profile) {
      return '';
    }

    const scores = [
      this.profile.puntajes.experiencia_concreta,
      this.profile.puntajes.observacion_reflexiva,
      this.profile.puntajes.conceptualizacion_abstracta,
      this.profile.puntajes.experimentacion_activa
    ];

    const centerX = 160;
    const centerY = 160;
    const radius = 110;

    const points = scores.map((score, index) => {
      const angle = (-Math.PI / 2) + (index * (Math.PI / 2));
      const scaled = (score / 100) * radius;
      const x = centerX + Math.cos(angle) * scaled;
      const y = centerY + Math.sin(angle) * scaled;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

    return points.join(' ');
  }
}
