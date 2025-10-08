'use client';

import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/contexts/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [nameError, setNameError] = useState('');

  const { login, register } = useAuth();

  const validateEmail = (email: string) => {
    if (!email.trim()) {
      setEmailError('Please enter your email.');
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setEmailError('Please enter a valid email format.');
      return false;
    }
    setEmailError('');
    return true;
  };

  const validatePassword = (password: string) => {
    if (!password) {
      setPasswordError('Please enter your password.');
      return false;
    }
    if (!isLogin && password.length < 6) {
      setPasswordError('Password must be at least 6 characters long.');
      return false;
    }
    setPasswordError('');
    return true;
  };

  const validateName = (name: string) => {
    if (!isLogin) {
      if (!name.trim()) {
        setNameError('Please enter your name.');
        return false;
      }
      if (name.trim().length < 2) {
        setNameError('Name must be at least 2 characters long.');
        return false;
      }
    }
    setNameError('');
    return true;
  };

  const validateForm = () => {
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);
    const isNameValid = validateName(name);

    return isEmailValid && isPasswordValid && isNameValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      let result;
      if (isLogin) {
        result = await login(email, password);
      } else {
        result = await register(email, password, name);
      }

      if (result.success) {
        onClose();
        setEmail('');
        setPassword('');
        setName('');
      } else {
        setError(result.error || '오류가 발생했습니다.');
      }
    } catch {
      setError('예상치 못한 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setEmailError('');
    setPasswordError('');
    setNameError('');
    setEmail('');
    setPassword('');
    setName('');
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="modern-title text-stone-700">
            {isLogin ? 'Sign In' : 'Sign Up'}
          </DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div className="space-y-2">
              <Label htmlFor="name" className="text-stone-600 font-normal">Name</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  validateName(e.target.value);
                }}
                placeholder="Enter your name"
                required={!isLogin}
                className={`soft-input ${nameError ? 'border-red-500' : ''}`}
              />
              {nameError && (
                <p className="text-red-500 text-sm">{nameError}</p>
              )}
            </div>
          )}
          
          <div className="space-y-2">
            <Label htmlFor="email" className="text-stone-600 font-normal">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                validateEmail(e.target.value);
              }}
              placeholder="Enter your email"
              required
              className={`soft-input ${emailError ? 'border-red-500' : ''}`}
            />
            {emailError && (
              <p className="text-red-500 text-sm">{emailError}</p>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password" className="text-stone-600 font-normal">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                validatePassword(e.target.value);
              }}
              placeholder="Enter your password"
              required
              className={`soft-input ${passwordError ? 'border-red-500' : ''}`}
            />
            {passwordError && (
              <p className="text-red-500 text-sm">{passwordError}</p>
            )}
          </div>

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}

          <div className="flex flex-col space-y-2">
            <Button type="submit" disabled={loading} className="w-full soft-button">
              {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
            </Button>
            
            <Button
              type="button"
              variant="outline"
              onClick={switchMode}
              className="w-full soft-button"
            >
              {isLogin ? 'Create Account' : 'Already have an account?'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
