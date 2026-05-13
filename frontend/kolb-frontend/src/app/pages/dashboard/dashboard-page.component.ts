import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { catchError, finalize, of, timeout } from 'rxjs';

import { ChatComponent } from '../../components/chat/chat.component';
import { KolbProfileComponent } from '../../components/kolb-profile/kolb-profile.component';
import { UserDataComponent } from '../../components/user-data/user-data.component';
import { AuthService } from '../../core/auth.service';
import { KolbService } from '../../core/kolb.service';


type DashboardSection = 'user' | 'kolb' | 'chat';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    UserDataComponent,
    KolbProfileComponent,
    ChatComponent
  ],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.scss'
})
export class DashboardPageComponent implements OnInit {
  selectedSection: DashboardSection = 'user';
  checkingProfile = true;
  kolbProfileExists = false;
  private checkingFallbackId: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private readonly authService: AuthService,
    private readonly kolbService: KolbService,
    private readonly router: Router
  ) {}

  ngOnInit(): void {
    this.startCheckingFallback();

    const user = this.authService.currentUser();
    if (!user) {
      this.finishChecking('user');
      return;
    }

    this.kolbService
      .getByUsernameOptional(user.username)
      .pipe(
        timeout(8000),
        catchError(() => of(null)),
        finalize(() => {
          this.finishChecking('kolb');
        })
      )
      .subscribe({
        next: (profile) => {
          this.kolbProfileExists = !!profile;
          this.selectedSection = 'kolb';
        }
      });
  }

  private startCheckingFallback(): void {
    this.clearCheckingFallback();
    this.checkingFallbackId = setTimeout(() => {
      this.finishChecking('kolb');
    }, 12000);
  }

  private clearCheckingFallback(): void {
    if (this.checkingFallbackId !== null) {
      clearTimeout(this.checkingFallbackId);
      this.checkingFallbackId = null;
    }
  }

  private finishChecking(defaultSection: DashboardSection): void {
    this.clearCheckingFallback();
    this.checkingProfile = false;
    if (this.selectedSection === 'user') {
      this.selectedSection = defaultSection;
    }
  }

  selectSection(section: DashboardSection): void {
    this.selectedSection = section;
  }

  logout(): void {
    this.clearCheckingFallback();
    this.authService.logout();
    this.router.navigate(['/auth']);
  }
}