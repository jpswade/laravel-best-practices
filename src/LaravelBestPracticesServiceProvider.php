<?php

declare(strict_types=1);

namespace Jpswade\LaravelBestPractices;

use Illuminate\Support\ServiceProvider;

final class LaravelBestPracticesServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        $pintSource = __DIR__ . '/../pint.json';
        $phpstanSource = __DIR__ . '/../phpstan.neon.dist';
        $aiignoreSource = __DIR__ . '/../.aiignore';

        $this->publishes([
            $pintSource => base_path('pint.json'),
        ], 'laravel-best-practices-pint');

        $this->publishes([
            $phpstanSource => base_path('phpstan.neon.dist'),
        ], 'laravel-best-practices-phpstan');

        $this->publishes([
            $aiignoreSource => base_path('.aiignore'),
        ], 'laravel-best-practices-aiignore');

        // Host exclusions are deliberately opt-in, outside the legacy all tag.
        foreach (['cursorignore', 'aiexclude', 'geminiignore'] as $hostFile) {
            $this->publishes([
                __DIR__ . '/../resources/host-controls/' . $hostFile => base_path('.' . $hostFile),
            ], 'laravel-best-practices-' . $hostFile);
        }

        $this->publishes([
            $pintSource => base_path('pint.json'),
            $phpstanSource => base_path('phpstan.neon.dist'),
            $aiignoreSource => base_path('.aiignore'),
        ], 'laravel-best-practices-all');
    }
}
