import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import { AuthService } from '../../core/auth.service';
import { UserService } from '../../core/user.service';

@Component({
  selector: 'app-user-data',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule
  ],
  templateUrl: './user-data.component.html',
  styleUrl: './user-data.component.scss'
})
export class UserDataComponent implements OnInit {
  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    dni: ['', Validators.required],
    nombre: ['', Validators.required],
    apellido: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    telefono: ['', Validators.required],
    password: ['']
  });

  saving = false;

  constructor(
    private readonly authService: AuthService,
    private readonly userService: UserService,
    private readonly snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    const user = this.authService.currentUser();
    if (!user) {
      return;
    }

    this.form.patchValue({
      dni: user.dni,
      nombre: user.nombre,
      apellido: user.apellido,
      email: user.email,
      telefono: user.telefono
    });
  }

  get username(): string {
    return this.authService.currentUser()?.username ?? '-';
  }

  onSave(): void {
    const user = this.authService.currentUser();
    if (!user || this.form.invalid || this.saving) {
      this.form.markAllAsTouched();
      return;
    }

    this.saving = true;
    const payload = this.form.getRawValue();
    this.userService.update(user.id, payload).subscribe({
      next: (updated) => {
        this.authService.setCurrentUser(updated);
        this.saving = false;
        this.form.patchValue({ password: '' });
        this.snackBar.open('Datos del usuario actualizados', 'Cerrar', { duration: 2500 });
      },
      error: (error) => {
        this.saving = false;
        const detail = error?.error?.detail || 'No se pudieron guardar los cambios';
        this.snackBar.open(detail, 'Cerrar', { duration: 3500 });
      }
    });
  }
}