"use client"

import { useState, useEffect } from "react"
import { NotesList } from "@/components/notes-list"
import { NoteEditor } from "@/components/note-editor"
import { Header } from "@/components/header"

export interface Note {
  id: string
  title: string
  content: string
  createdAt: number
  updatedAt: number
}

export default function NotesApp() {
  const [notes, setNotes] = useState<Note[]>([])
  const [selectedNote, setSelectedNote] = useState<Note | null>(null)
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    const savedNotes = localStorage.getItem("elegant-notes")
    if (savedNotes) {
      setNotes(JSON.parse(savedNotes))
    }
  }, [])

  useEffect(() => {
    localStorage.setItem("elegant-notes", JSON.stringify(notes))
  }, [notes])

  const createNote = () => {
    const newNote: Note = {
      id: Date.now().toString(),
      title: "",
      content: "",
      createdAt: Date.now(),
      updatedAt: Date.now(),
    }
    setNotes([newNote, ...notes])
    setSelectedNote(newNote)
    setIsCreating(true)
  }

  const updateNote = (id: string, updates: Partial<Note>) => {
    setNotes(notes.map((note) => (note.id === id ? { ...note, ...updates, updatedAt: Date.now() } : note)))
    if (selectedNote?.id === id) {
      setSelectedNote({ ...selectedNote, ...updates, updatedAt: Date.now() })
    }
  }

  const deleteNote = (id: string) => {
    setNotes(notes.filter((note) => note.id !== id))
    if (selectedNote?.id === id) {
      setSelectedNote(null)
    }
  }

  const handleNoteSelect = (note: Note) => {
    setSelectedNote(note)
    setIsCreating(false)
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <Header onNewNote={createNote} />
      <div className="flex flex-1 overflow-hidden">
        <NotesList
          notes={notes}
          selectedNote={selectedNote}
          onSelectNote={handleNoteSelect}
          onDeleteNote={deleteNote}
        />
        <NoteEditor note={selectedNote} onUpdateNote={updateNote} isCreating={isCreating} />
      </div>
    </div>
  )
}
