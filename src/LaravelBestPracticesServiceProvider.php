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

        $this->publishes([
            $pintSource => base_path('pint.json'),
            $phpstanSource => base_path('phpstan.neon.dist'),
            $aiignoreSource => base_path('.aiignore'),
        ], 'laravel-best-practices-all');
    }
}
