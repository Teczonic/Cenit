import type { IAuthService } from '../../domain/ports/IAuthService'
import type { UserRaw, LoginResponse } from '@lib/types'
import { apiFetch } from '@lib/api'
import { removeToken } from '@lib/auth'

export class AuthServiceImpl implements IAuthService {
  async login(username: string, password: string): Promise<LoginResponse> {
    return apiFetch<LoginResponse>('POST', '/api/auth/login', { username, password })
  }

  me(token: string): Promise<UserRaw> {
    return apiFetch<UserRaw>('GET', '/api/auth/me', undefined, token)
  }

  logout(): void {
    removeToken()
  }
}
