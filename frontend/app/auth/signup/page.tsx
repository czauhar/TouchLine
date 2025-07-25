'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { apiClient } from '../../../lib/auth'
import toast from 'react-hot-toast'

const signupSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  username: z.string().min(3, 'Username must be at least 3 characters'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  phone_number: z.string().optional(),
})

type SignupForm = z.infer<typeof signupSchema>

export default function SignupPage() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupForm>({
    resolver: zodResolver(signupSchema),
  })

  const onSubmit = async (data: SignupForm) => {
    setIsLoading(true)
    try {
      const res = await apiClient.register(data)
      // After successful registration, sign in
      await signIn('credentials', {
        email: data.email,
        password: data.password,
        redirect: false,
      })
      toast.success('Account created!')
      router.push('/dashboard')
    } catch (error: any) {
      toast.error(error.message || 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-black bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent mb-2">
            Create Account
          </h1>
          <p className="text-gray-400">Sign up for TouchLine</p>
        </div>
        <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label className="block text-gray-300 mb-1">Email</label>
              <input type="email" {...register('email')} className="w-full px-3 py-2 rounded border border-gray-700 bg-gray-800 text-white" />
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
            </div>
            <div>
              <label className="block text-gray-300 mb-1">Username</label>
              <input type="text" {...register('username')} className="w-full px-3 py-2 rounded border border-gray-700 bg-gray-800 text-white" />
              {errors.username && <p className="text-red-500 text-sm mt-1">{errors.username.message}</p>}
            </div>
            <div>
              <label className="block text-gray-300 mb-1">Password</label>
              <input type="password" {...register('password')} className="w-full px-3 py-2 rounded border border-gray-700 bg-gray-800 text-white" />
              {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>}
            </div>
            <div>
              <label className="block text-gray-300 mb-1">Phone (optional)</label>
              <input type="text" {...register('phone_number')} className="w-full px-3 py-2 rounded border border-gray-700 bg-gray-800 text-white" />
            </div>
            <button type="submit" disabled={isLoading} className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition">
              {isLoading ? 'Creating Account...' : 'Sign Up'}
            </button>
          </form>
          <div className="mt-6 text-center">
            <Link href="/auth/signin" className="text-blue-400 hover:underline">Already have an account? Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  )
} 