'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AuthModal from '@/components/AuthModal';
import MemoCard from '@/components/MemoCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Plus, Search, LogOut, User } from 'lucide-react';

interface Memo {
  id: string;
  title: string;
  content: string;
  tags: string[];
  color: string;
  updatedAt: string;
}

const pastelColors = [
  { name: 'Ivory', value: '#fefdf8' },
  { name: 'Cream', value: '#faf8f5' },
  { name: 'Off-White', value: '#f8f6f3' },
  { name: 'Warm Beige', value: '#f5f3f0' },
  { name: 'Soft Beige', value: '#f0ede8' },
  { name: 'Light Beige', value: '#ebe7e2' },
  { name: 'Muted Cream', value: '#f7f5f2' },
  { name: 'Soft White', value: '#faf9f7' },
  { name: 'Warm Ivory', value: '#fdfcf8' },
  { name: 'Pale Beige', value: '#f3f1ed' },
];

export default function HomePage() {
  const { user, loading, logout, api } = useAuth();
  const [memos, setMemos] = useState<Memo[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTag, setSelectedTag] = useState('');
  const [selectedColor, setSelectedColor] = useState('');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'title'>('newest');
  const [selectedMemo, setSelectedMemo] = useState<Memo | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editTags, setEditTags] = useState<string[]>([]);
  const [editColor, setEditColor] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);

  // API에서 메모 불러오기
  const loadMemos = useCallback(async () => {
    if (!user) return;
    
    try {
      const response = await api.get('/memos');
      setMemos(response.data);
    } catch (error) {
      console.error('Failed to load memos:', error);
    }
  }, [user, api]);

  useEffect(() => {
    if (user) {
      loadMemos();
    } else {
      setMemos([]);
    }
  }, [user, loadMemos]);

  // 새 메모 생성
  const createNewMemo = async () => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    try {
      const response = await api.post('/memos', {
        title: '새 메모',
        content: '',
        tags: [],
        color: pastelColors[0].value, // 기본적으로 Ivory 색상 사용
      });
      
      const newMemo = response.data;
      setMemos([newMemo, ...memos]);
      setSelectedMemo(newMemo); // 새 메모를 자동으로 선택
      setEditTitle(newMemo.title);
      setEditContent(newMemo.content);
      setEditTags(newMemo.tags);
      setEditColor(newMemo.color);
      setIsEditing(true); // 새 메모는 자동으로 편집 모드로 시작
      
      // 성공 메시지 (선택사항)
      console.log('새 메모가 생성되었습니다.');
    } catch (error) {
      console.error('Failed to create memo:', error);
      alert('메모 생성에 실패했습니다. 다시 시도해주세요.');
    }
  };

  // 메모 업데이트
  const updateMemo = async (id: string, data: Partial<Memo>) => {
    try {
      const response = await api.put(`/memos/${id}`, data);
      const updatedMemo = response.data;
      setMemos(memos.map(memo => 
        memo.id === id ? updatedMemo : memo
      ));
      
      // 선택된 메모가 업데이트된 경우 상태도 업데이트
      if (selectedMemo?.id === id) {
        setSelectedMemo(updatedMemo);
      }
      
      console.log('메모가 업데이트되었습니다.');
    } catch (error) {
      console.error('Failed to update memo:', error);
      alert('메모 업데이트에 실패했습니다. 다시 시도해주세요.');
    }
  };

  // 메모 삭제
  const deleteMemo = async (id: string) => {
    try {
      await api.delete(`/memos/${id}`);
      setMemos(memos.filter(memo => memo.id !== id));
      
      // 선택된 메모가 삭제된 경우 선택 해제 및 편집 모드 종료
      if (selectedMemo?.id === id) {
        setSelectedMemo(null);
        setIsEditing(false);
        setEditTitle('');
        setEditContent('');
        setEditTags([]);
        setEditColor('');
      }
      
      console.log('메모가 삭제되었습니다.');
    } catch (error) {
      console.error('Failed to delete memo:', error);
      alert('메모 삭제에 실패했습니다. 다시 시도해주세요.');
    }
  };

  // 검색 및 필터링
  const filteredMemos = useMemo(() => {
    let filtered = memos.filter(memo => {
      const matchesSearch = memo.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        memo.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        memo.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesTag = !selectedTag || memo.tags.includes(selectedTag);
      const matchesColor = !selectedColor || memo.color === selectedColor;
      
      return matchesSearch && matchesTag && matchesColor;
    });

    // 정렬
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
        case 'oldest':
          return new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime();
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    return filtered;
  }, [memos, searchTerm, selectedTag, selectedColor, sortBy]);

  // 모든 태그 가져오기
  const getAllTags = () => {
    const allTags = new Set<string>();
    memos.forEach(memo => {
      memo.tags.forEach(tag => allTags.add(tag));
    });
    return Array.from(allTags).sort();
  };

  // 필터 초기화
  const clearFilters = () => {
    setSearchTerm('');
    setSelectedTag('');
    setSelectedColor('');
    setSortBy('newest');
  };

  // 편집 모드 시작
  const startEditing = () => {
    if (!selectedMemo) return;
    setEditTitle(selectedMemo.title);
    setEditContent(selectedMemo.content);
    setEditTags(selectedMemo.tags);
    setEditColor(selectedMemo.color);
    setIsEditing(true);
  };

  // 편집 모드 취소
  const cancelEditing = () => {
    setIsEditing(false);
    setEditTitle('');
    setEditContent('');
    setEditTags([]);
    setEditColor('');
  };

  // 편집 저장
  const saveEditing = async () => {
    if (!selectedMemo) return;

    try {
      await updateMemo(selectedMemo.id, {
        title: editTitle,
        content: editContent,
        tags: editTags,
        color: editColor,
      });
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to save memo:', error);
      alert('메모 저장에 실패했습니다.');
    }
  };

  // 태그 입력 처리
  const handleTagInput = (value: string) => {
    const tags = value.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
    setEditTags(tags);
  };

  // 태그 입력 필드 값
  const tagInputValue = editTags.join(', ');

  // 검색어 초기화
  const clearSearch = () => {
    setSearchTerm('');
  };

  // 키보드 단축키 처리
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 's' && isEditing) {
        e.preventDefault();
        saveEditing();
      } else if (e.key === 'Escape' && isEditing) {
        cancelEditing();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isEditing, editTitle, editContent, editTags, editColor, selectedMemo]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen paper-texture">
      {/* Header */}
      <header className="bg-white/60 backdrop-blur-md shadow-sm border-b border-stone-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
                <h1 className="text-3xl font-light modern-title text-stone-700">📝 Notes</h1>
            </div>
            
            {user ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <User className="w-5 h-5 text-stone-500" />
                  <span className="text-stone-600 font-normal">Hello, {user.name}!</span>
                </div>
                <Button onClick={logout} variant="outline" size="sm" className="soft-button">
                  <LogOut className="w-4 h-4 mr-1" />
                  Sign Out
                </Button>
              </div>
            ) : (
              <Button onClick={() => setShowAuthModal(true)} className="soft-button">
                Sign In
              </Button>
            )}
          </div>
        </div>
      </header>

      <main className="flex h-[calc(100vh-4rem)]">
        {!user ? (
          <div className="flex-1 flex items-center justify-center">
            <Card className="max-w-md mx-auto memo-card-cream">
              <CardContent className="pt-6">
                <h2 className="text-3xl font-light modern-title text-stone-700 mb-4">
                  Welcome to MemoPad!
                </h2>
                <p className="text-stone-600 mb-6 font-normal">
                  Sign in to create and manage your personal notes.
                </p>
                <Button onClick={() => setShowAuthModal(true)} size="lg" className="w-full soft-button">
                  Get Started
                </Button>
              </CardContent>
            </Card>
          </div>
        ) : (
          <>
            {/* 사이드바 */}
            <div className="w-80 bg-white/80 backdrop-blur-sm border-r border-stone-200/50 flex flex-col">
              {/* 사이드바 헤더 */}
              <div className="p-6 border-b border-stone-200/50">
                <h2 className="text-2xl font-light modern-title text-stone-700 mb-2">Notes</h2>
                <p className="text-sm text-stone-500 font-normal">{memos.length} notes</p>
              </div>

              {/* 검색 바 */}
              <div className="p-4 border-b border-stone-200/30">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-stone-400 w-4 h-4" />
                  <Input
                    type="text"
                    placeholder="Search notes..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-10 soft-input"
                  />
                  {searchTerm && (
                    <button
                      onClick={clearSearch}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-stone-400 hover:text-stone-600 transition-colors"
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>

              {/* 필터 옵션 */}
              <div className="p-4 border-b border-stone-200/30 space-y-3">
                <div className="flex items-center gap-2">
                  <label className="text-xs font-normal text-stone-500 uppercase tracking-wide">Tags</label>
                  <select
                    value={selectedTag}
                    onChange={(e) => setSelectedTag(e.target.value)}
                    className="flex-1 px-2 py-1.5 border border-stone-200 rounded-md focus:outline-none text-sm soft-filter"
                  >
                    <option value="">All Tags</option>
                    {getAllTags().map(tag => (
                      <option key={tag} value={tag}>{tag}</option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <label className="text-xs font-normal text-stone-500 uppercase tracking-wide">Color</label>
                  <select
                    value={selectedColor}
                    onChange={(e) => setSelectedColor(e.target.value)}
                    className="flex-1 px-2 py-1.5 border border-stone-200 rounded-md focus:outline-none text-sm soft-filter"
                  >
                    <option value="">All Colors</option>
                    {pastelColors.map((color, index) => (
                      <option key={index} value={color.value}>
                        {color.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <label className="text-xs font-normal text-stone-500 uppercase tracking-wide">Sort</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'newest' | 'oldest' | 'title')}
                    className="flex-1 px-2 py-1.5 border border-stone-200 rounded-md focus:outline-none text-sm soft-filter"
                  >
                    <option value="newest">Newest</option>
                    <option value="oldest">Oldest</option>
                    <option value="title">Title</option>
                  </select>
                </div>

                <Button
                  onClick={clearFilters}
                  variant="outline"
                  size="sm"
                  className="w-full soft-button text-xs"
                >
                  Clear Filters
                </Button>
              </div>

              {/* 메모 목록 */}
              <div className="flex-1 overflow-y-auto">
                {filteredMemos.length === 0 ? (
                  <div className="p-6 text-center">
                    <div className="text-stone-500 text-sm font-light">
                      {searchTerm || selectedTag || selectedColor ? 
                        'No notes match your search.' : 
                        'No notes yet.'
                      }
                    </div>
                  </div>
                ) : (
                  <div className="p-2">
                    {filteredMemos.map(memo => (
                      <div
                        key={memo.id}
                        className={`p-4 mb-2 rounded-lg cursor-pointer transition-colors border ${
                          selectedMemo?.id === memo.id
                            ? 'border-stone-300/50'
                            : 'border-stone-200/30 hover:border-stone-300/40'
                        }`}
                        style={{ 
                          backgroundColor: memo.color,
                          borderColor: selectedMemo?.id === memo.id ? 'rgba(120, 110, 100, 0.3)' : 'rgba(120, 110, 100, 0.15)'
                        }}
                        onClick={() => {
                          setSelectedMemo(memo);
                          setIsEditing(false);
                        }}
                      >
                        <h3 className="font-medium text-stone-800 text-sm mb-1 line-clamp-1">
                          {memo.title}
                        </h3>
                        <p className="text-xs text-stone-600 line-clamp-2 mb-2">
                          {memo.content}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-stone-400">
                            {new Date(memo.updatedAt).toLocaleDateString()}
                          </span>
                          {memo.tags.length > 0 && (
                            <div className="flex gap-1">
                              {memo.tags.slice(0, 2).map((tag, index) => (
                                <span key={index} className="text-xs text-stone-500 bg-stone-200/50 px-1.5 py-0.5 rounded">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* 새 메모 버튼 */}
              <div className="p-4 border-t border-stone-200/50">
                <Button onClick={createNewMemo} className="w-full soft-button">
                  <Plus className="w-4 h-4 mr-2" />
                  New Note
                </Button>
              </div>
            </div>

            {/* 메인 콘텐츠 영역 */}
            <div className="flex-1 bg-white/60 backdrop-blur-sm">
              {selectedMemo ? (
                <div className="h-full flex flex-col">
                  {isEditing ? (
                    // 편집 모드
                    <>
                      <div 
                        className="p-6 border-b border-stone-200/50"
                        style={{ backgroundColor: editColor }}
                      >
                        <Input
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          placeholder="Enter title..."
                          className="text-2xl font-light modern-title text-stone-700 mb-4 soft-input"
                        />
                        <div className="flex items-center gap-4 text-sm text-stone-500">
                          <span>Last updated: {new Date(selectedMemo.updatedAt).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div 
                        className="flex-1 p-6 overflow-y-auto"
                        style={{ backgroundColor: editColor }}
                      >
                        <div className="space-y-4">
                          <div>
                            <label className="text-xs font-normal text-stone-500 uppercase tracking-wide mb-2 block">
                              Tags (comma separated)
                            </label>
                            <Input
                              value={tagInputValue}
                              onChange={(e) => handleTagInput(e.target.value)}
                              placeholder="Enter tags separated by commas..."
                              className="soft-input"
                            />
                          </div>
                          <div>
                            <label className="text-xs font-normal text-stone-500 uppercase tracking-wide mb-2 block">
                              Color
                            </label>
                            <div className="flex gap-2 flex-wrap">
                              {pastelColors.map((color, index) => (
                                <button
                                  key={index}
                                  onClick={() => setEditColor(color.value)}
                                  className={`w-8 h-8 rounded-full border-2 ${
                                    editColor === color.value ? 'border-stone-600' : 'border-stone-300'
                                  }`}
                                  style={{ backgroundColor: color.value }}
                                  title={color.name}
                                />
                              ))}
                            </div>
                          </div>
                          <div>
                            <label className="text-xs font-normal text-stone-500 uppercase tracking-wide mb-2 block">
                              Content
                            </label>
                            <textarea
                              value={editContent}
                              onChange={(e) => setEditContent(e.target.value)}
                              placeholder="Enter content..."
                              className="w-full h-96 p-3 border border-stone-200 rounded-md focus:outline-none focus:ring-2 focus:ring-stone-300 soft-input resize-none"
                            />
                          </div>
                        </div>
                      </div>
                      <div className="p-4 border-t border-stone-200/50">
                        <div className="flex gap-2">
                          <Button onClick={saveEditing} className="soft-button">
                            Save (Ctrl+S)
                          </Button>
                          <Button onClick={cancelEditing} variant="outline" className="soft-button">
                            Cancel (Esc)
                          </Button>
                        </div>
                      </div>
                    </>
                  ) : (
                    // 읽기 모드
                    <>
                      <div 
                        className="p-6 border-b border-stone-200/50"
                        style={{ backgroundColor: selectedMemo.color }}
                      >
                        <h2 className="text-2xl font-light modern-title text-stone-700 mb-2">
                          {selectedMemo.title}
                        </h2>
                        <div className="flex items-center gap-4 text-sm text-stone-500">
                          <span>Last updated: {new Date(selectedMemo.updatedAt).toLocaleDateString()}</span>
                          {selectedMemo.tags.length > 0 && (
                            <div className="flex gap-1">
                              {selectedMemo.tags.map((tag, index) => (
                                <span key={index} className="bg-stone-200/50 px-2 py-1 rounded text-xs">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                      <div 
                        className="flex-1 p-6 overflow-y-auto"
                        style={{ backgroundColor: selectedMemo.color }}
                      >
                        <div className="prose prose-stone max-w-none">
                          <div className="whitespace-pre-wrap text-stone-700 leading-relaxed">
                            {selectedMemo.content}
                          </div>
                        </div>
                      </div>
                      <div className="p-4 border-t border-stone-200/50">
                        <div className="flex gap-2">
                          <Button onClick={startEditing} className="soft-button">
                            Edit
                          </Button>
                          <Button
                            onClick={() => deleteMemo(selectedMemo.id)}
                            variant="outline"
                            className="soft-button"
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-xl font-light text-stone-600 mb-2">Select a note to begin</h3>
                    <p className="text-sm text-stone-500 font-normal">
                      Choose a note from the sidebar or create a new one to start writing
                    </p>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </main>
      
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
      />
    </div>
  );
}