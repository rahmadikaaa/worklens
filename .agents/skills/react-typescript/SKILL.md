---
name: react-typescript
description: Modern React and TypeScript frontend development. Use when developing, refactoring, or reviewing React components, TypeScript interfaces, Tailwind CSS styling, Vite build configurations, and frontend API clients.
---

# React & TypeScript Engineering

## Overview

Modern, type-safe, and responsive frontend development using React 18+, TypeScript, Vite, and Tailwind CSS. Emphasizes clean component architecture, strict type contracts, and zero-bloat state management.

## Core Principles

1. **Strict Type Safety:**
   - Define domain interfaces in `src/types/` matching backend API schemas.
   - Avoid `any` at all costs. Use discriminated unions for status flags and state transitions.
   - Type component props explicitly with `React.FC<Props>` or directly typed parameters.

2. **Component Decomposition:**
   - Keep components focused and under 150 lines. Split large tables, modals, and metric panels into dedicated child components in `src/components/`.
   - Separate presentational UI from data fetching logic using custom hooks.

3. **State Management (Smallest Complete Solution):**
   - Rely on React native state (`useState`, `useReducer`, `useContext`) before adding external state libraries like Redux or Zustand.
   - For server-synced state, manage loading, success, and error states defensively.

4. **Tailwind CSS Utility Discipline:**
   - Use standard Tailwind utility classes consistently.
   - Avoid inline styles. Rely on Tailwind responsive prefixes (`sm:`, `md:`, `lg:`) and pseudo-classes (`hover:`, `focus:`).

5. **API & Error Boundaries:**
   - Wrap fetch calls with structured error handling.
   - Provide visual fallbacks (skeletons, spinners, banner alerts) for pending or failed network requests.

