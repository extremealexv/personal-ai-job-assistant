import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MappingEngine } from '../Engine';
import { LeverStrategy } from '../../ats/LeverStrategy';

describe('Mapping Engine & Strategies', () => {
    let engine: MappingEngine;

    beforeEach(() => {
        engine = new MappingEngine();
        
        // Mock the window location for JS DOM testing
        Object.defineProperty(window, 'location', {
            value: { href: 'https://jobs.lever.co/lever' },
            writable: true
        });
    });

    it('should accurately detect the Lever ATS from jobs.lever.co URLs', () => {
        const strategy = engine.detectStrategy();
        expect(strategy).toBeInstanceOf(LeverStrategy);
    });

    it('should extract correct static field mappings from Lever defaults', () => {
        const strategy = new LeverStrategy();
        const map = strategy.getFieldMap();
        expect(map.firstName).toBe('input[name="filter-first-name"], input[name="name"]');
        expect(map.email).toBe('input[name="email"]');
    });

    it('should return false when executeFill targets unsupported domains', () => {
        Object.defineProperty(window, 'location', {
            value: { href: 'https://random-website.com' },
            writable: true
        });
        const result = engine.executeFill({});
        expect(result).toBe(false);
    });

    it('should instantiate MutationObserver for SPA forms and trigger executeFill on significant mutations', async () => {
        vi.useFakeTimers();
        const executeSpy = vi.spyOn(engine, 'executeFill').mockReturnValue(true);
        const observer = engine.observeSPAForms({});
        
        // Mock the button presence implicitly
        const btn = document.createElement('button');
        btn.textContent = 'Next Page';
        document.body.appendChild(btn);
        
        // Let JSDOM flush the microtask queue before advancing timers
        await Promise.resolve();
        
        vi.advanceTimersByTime(1100);
        
        // Expect debouncer fired
        expect(executeSpy).toHaveBeenCalled();
        
        observer.disconnect();
        vi.useRealTimers();
    });
});
