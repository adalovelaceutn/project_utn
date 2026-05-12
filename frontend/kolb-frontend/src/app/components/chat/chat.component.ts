import { CommonModule } from '@angular/common';
import { AfterViewInit, ChangeDetectorRef, Component, ElementRef, inject, NgZone, ViewChild } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { finalize, take } from 'rxjs';

import { ChatService } from '../../core/chat.service';
import { ChatMessage } from '../../core/models';
import { KolbService } from '../../core/kolb.service';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatSnackBarModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent {
  private readonly fb = inject(FormBuilder);
  private readonly snackBar = inject(MatSnackBar);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly zone = inject(NgZone);
  @ViewChild('chatWindow') private chatWindow?: ElementRef<HTMLDivElement>;
  private sessionId: string | null = null;
  loading = false;

  readonly form = this.fb.nonNullable.group({
    message: ['', Validators.required]
  });

  messages: ChatMessage[] = [
    {
      role: 'assistant',
      text: 'Hola, soy Qolby. Cuando quieras, empezamos la entrevista para construir tu perfil de aprendizaje.',
      timestamp: new Date()
    }
  ];

  constructor(
    private readonly chatService: ChatService,
    private readonly kolbService: KolbService,
    private readonly authService: AuthService
  ) {}

  ngOnInit(): void {
    this.startInterviewIfNeeded();
  }

  ngAfterViewInit(): void {
    this.scrollChatToBottom();
  }

  private scrollChatToBottom(): void {
    setTimeout(() => {
      const element = this.chatWindow?.nativeElement;
      if (!element) {
        return;
      }
      element.scrollTop = element.scrollHeight;
    });
  }

  private runUiUpdate(update: () => void): void {
    this.zone.run(() => {
      update();
      this.cdr.detectChanges();
    });
  }

  private startInterviewIfNeeded(): void {
    const user = this.authService.currentUser();
    if (!user || this.loading || this.sessionId) {
      return;
    }

    this.kolbService.getByUsernameOptional(user.username).pipe(take(1)).subscribe({
      next: (profile) => {
        if (profile) {
          return;
        }

        this.runUiUpdate(() => {
          this.messages = [
            ...this.messages,
            {
              role: 'assistant',
              text: 'No detecte un perfil Kolb previo. Inicio la entrevista ahora.',
              timestamp: new Date()
            }
          ];
        });
        this.scrollChatToBottom();

        this.loading = true;
        this.chatService.sendMessage('Iniciar entrevista Kolb', this.sessionId)
          .pipe(finalize(() => {
            this.runUiUpdate(() => {
              this.loading = false;
            });
          }))
          .subscribe({
            next: (response) => {
              this.runUiUpdate(() => {
                this.sessionId = response.session_id;
                this.messages = [
                  ...this.messages,
                  { role: 'assistant', text: response.reply, timestamp: new Date() }
                ];
              });
              this.scrollChatToBottom();
            },
            error: (error) => {
              const detail = error?.error?.detail || error?.message || 'No se pudo iniciar la entrevista con el agente principal.';
              this.runUiUpdate(() => {
                this.messages = [
                  ...this.messages,
                  {
                    role: 'assistant',
                    text: 'No pude iniciar la entrevista en este momento. Intenta nuevamente en unos segundos.',
                    timestamp: new Date()
                  }
                ];
              });
              this.scrollChatToBottom();
              this.snackBar.open(detail, 'Cerrar', { duration: 4000 });
            }
          });
      },
      error: () => {
        // Si no se puede verificar el perfil, el usuario puede iniciar manualmente desde el input.
      }
    });
  }

  sendMessage(): void {
    if (this.loading) {
      return;
    }

    const activeElement = document.activeElement;
    if (activeElement instanceof HTMLElement) {
      activeElement.blur();
    }

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const userText = this.form.getRawValue().message.trim();
    if (!userText) {
      return;
    }

    this.runUiUpdate(() => {
      this.messages = [
        ...this.messages,
        { role: 'user', text: userText, timestamp: new Date() },
      ];
    });
    this.scrollChatToBottom();

    this.runUiUpdate(() => {
      this.loading = true;
    });
    this.chatService.sendMessage(userText, this.sessionId)
      .pipe(finalize(() => {
        this.runUiUpdate(() => {
          this.loading = false;
        });
      }))
      .subscribe({
        next: (response) => {
          this.runUiUpdate(() => {
            this.sessionId = response.session_id;
            this.messages = [
              ...this.messages,
              { role: 'assistant', text: response.reply, timestamp: new Date() }
            ];
          });
          this.scrollChatToBottom();
        },
        error: (error) => {
          const detail = error?.error?.detail || error?.message || 'No se pudo conectar con el agente principal.';
          this.runUiUpdate(() => {
            this.messages = [
              ...this.messages,
              {
                role: 'assistant',
                text: 'No pude continuar la entrevista en este momento. Intenta nuevamente en unos segundos.',
                timestamp: new Date()
              }
            ];
          });
          this.scrollChatToBottom();
          this.snackBar.open(detail, 'Cerrar', { duration: 4000 });
        }
      });

    this.form.reset();
  }
}