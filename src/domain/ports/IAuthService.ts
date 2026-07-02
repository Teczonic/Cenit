import type { UserRaw, LoginResponse } from '@lib/types'

export interface IAuthService {
  login(username: string, password: string): Promise<LoginResponse>
  me(token: string): Promise<UserRaw>
  logout(): void
}
