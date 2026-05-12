import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-auth-page',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatTabsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule
  ],
  templateUrl: './auth-page.component.html',
  styleUrl: './auth-page.component.scss'
})
export class AuthPageComponent {
  private readonly fb = inject(FormBuilder);

  readonly loginForm = this.fb.nonNullable.group({
    username: ['', [Validators.required]],
    password: ['', [Validators.required]]
  });

  readonly registerForm = this.fb.nonNullable.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    dni: ['', [Validators.required]],
    nombre: ['', [Validators.required]],
    apellido: ['', [Validators.required]],
    email: ['', [Validators.required, Validators.email]],
    telefono: ['', [Validators.required]]
  });

  readonly loadingLogin = signal(false);
  readonly loadingRegister = signal(false);

  constructor(
    private readonly authService: AuthService,
    private readonly router: Router,
    private readonly snackBar: MatSnackBar
  ) {}

  onLogin(): void {
    if (this.loginForm.invalid || this.loadingLogin()) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.loadingLogin.set(true);
    this.authService.login(this.loginForm.getRawValue()).subscribe({
      next: () => {
        this.loadingLogin.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        this.loadingLogin.set(false);
        const detail = error?.error?.detail || 'No se pudo iniciar sesion';
        this.snackBar.open(detail, 'Cerrar', { duration: 3500 });
      }
    });
  }

  onRegister(): void {
    if (this.registerForm.invalid || this.loadingRegister()) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.loadingRegister.set(true);
    this.authService.register(this.registerForm.getRawValue()).subscribe({
      next: () => {
        this.loadingRegister.set(false);
        this.registerForm.reset();
        this.snackBar.open('Usuario creado. Ahora puedes iniciar sesion.', 'Cerrar', { duration: 3500 });
      },
      error: (error) => {
        this.loadingRegister.set(false);
        const detail = error?.error?.detail || 'No se pudo crear el usuario';
        this.snackBar.open(detail, 'Cerrar', { duration: 3500 });
      }
    });
  }
}