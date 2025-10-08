'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Edit2, Save, X, Trash2 } from 'lucide-react';

interface Memo {
  id: string;
  title: string;
  content: string;
  tags: string[];
  color: string;
  updatedAt: string;
}

interface MemoCardProps {
  memo: Memo;
  onUpdate: (id: string, data: Partial<Memo>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
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

export default function MemoCard({ memo, onUpdate, onDelete }: MemoCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(memo.title);
  const [content, setContent] = useState(memo.content);
  const [tags, setTags] = useState(memo.tags.join(', '));
  const [color, setColor] = useState(memo.color);

  const handleSave = async () => {
    if (!title.trim() && !content.trim()) {
      alert('제목 또는 내용을 입력해주세요.');
      return;
    }

    const tagsArray = tags.trim() 
      ? tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      : [];

    await onUpdate(memo.id, {
      title: title.trim() || '제목 없음',
      content: content.trim(),
      tags: tagsArray,
      color,
    });

    setIsEditing(false);
  };

  // 키보드 단축키 처리
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleCancel();
    } else if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSave();
    }
  };

  const handleCancel = () => {
    setTitle(memo.title);
    setContent(memo.content);
    setTags(memo.tags.join(', '));
    setColor(memo.color);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (window.confirm('정말로 이 메모를 삭제하시겠습니까?')) {
      await onDelete(memo.id);
    }
  };

  return (
    <Card
      className="w-full transition-all duration-200 hover:shadow-lg memo-card-cream"
      style={{ backgroundColor: color }}
    >
      <CardHeader className="pb-3">
        {isEditing ? (
              <div className="space-y-3" onKeyDown={handleKeyDown}>
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter title..."
                  className="font-semibold soft-input"
                />
                <div className="space-y-2">
                  <label className="text-xs font-normal text-stone-500 uppercase tracking-wide">Tags (comma separated)</label>
                  <Input
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="Enter tags separated by commas..."
                    className="soft-input"
                  />
                </div>
            <div className="space-y-2">
              <label className="text-xs font-normal text-stone-500 uppercase tracking-wide">Color</label>
              <div className="flex flex-wrap gap-2">
                {pastelColors.map((colorOption, index) => (
                  <button
                    key={index}
                    className={`w-8 h-8 rounded-full border-2 ${
                      color === colorOption.value ? 'border-stone-600' : 'border-stone-300'
                    }`}
                    style={{ backgroundColor: colorOption.value }}
                    onClick={() => setColor(colorOption.value)}
                    title={colorOption.name}
                  />
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <CardTitle className="text-lg">{memo.title || '제목 없음'}</CardTitle>
            {memo.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {memo.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    #{tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )}
      </CardHeader>
      
      <CardContent className="pt-0">
        {isEditing ? (
          <div className="space-y-3">
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter content..."
              className="min-h-[100px] resize-none soft-input"
            />
            <div className="flex gap-2">
              <Button onClick={handleSave} size="sm" className="flex-1 soft-button">
                <Save className="w-4 h-4 mr-1" />
                Save (Ctrl+S)
              </Button>
              <Button onClick={handleCancel} size="sm" variant="outline" className="flex-1 soft-button">
                <X className="w-4 h-4 mr-1" />
                Cancel (Esc)
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-gray-700 whitespace-pre-wrap">{memo.content}</p>
            <div className="flex justify-between items-center text-xs text-gray-500">
              <span>
                {new Date(memo.updatedAt).toLocaleString('ko-KR')}
              </span>
              <div className="flex gap-1">
                <Button
                  onClick={() => setIsEditing(true)}
                  size="sm"
                  variant="ghost"
                  className="h-8 px-2 soft-button"
                >
                  <Edit2 className="w-4 h-4" />
                </Button>
                <Button
                  onClick={handleDelete}
                  size="sm"
                  variant="ghost"
                  className="h-8 px-2 soft-button text-red-500 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
