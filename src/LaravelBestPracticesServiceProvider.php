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

        $this->publishes([
            $pintSource => base_path('pint.json'),
        ], 'laravel-best-practices-pint');

        $this->publishes([
            $phpstanSource => base_path('phpstan.neon.dist'),
        ], 'laravel-best-practices-phpstan');

        $this->publishes([
            $pintSource => base_path('pint.json'),
            $phpstanSource => base_path('phpstan.neon.dist'),
        ], 'laravel-best-practices-all');
    }
}
