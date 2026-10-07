<?php

declare(strict_types=1);

use Symfony\Component\Yaml\Exception\ParseException;
use Symfony\Component\Yaml\Yaml;

require dirname(__DIR__).'/vendor/autoload.php';

$root = dirname(__DIR__).'/resources/boost/skills';
$allowed = ['name', 'description', 'license', 'compatibility', 'metadata'];
$errors = [];
$skills = glob($root.'/*/SKILL.md') ?: [];

if ($skills === []) {
    $errors[] = 'No skills found';
}

foreach ($skills as $path) {
    $content = file_get_contents($path);

    if ($content === false || preg_match('/\A---\R(.*?)\R---\R/s', $content, $match) !== 1) {
        $errors[] = "{$path}: missing frontmatter";

        continue;
    }

    try {
        $meta = Yaml::parse($match[1], Yaml::PARSE_OBJECT_FOR_MAP);
    } catch (ParseException $exception) {
        $errors[] = "{$path}: {$exception->getMessage()}";

        continue;
    }

    if (($meta instanceof stdClass) === false) {
        $errors[] = "{$path}: frontmatter must be a mapping";

        continue;
    }

    $meta = (array) $meta;
    $unsupported = array_diff(array_keys($meta), $allowed);

    if ($unsupported !== []) {
        $errors[] = "{$path}: unsupported portable metadata: ".implode(', ', $unsupported);
    }

    $name = $meta['name'] ?? '';

    if (
        is_string($name) === false
        || preg_match('/\A[a-z0-9]+(?:-[a-z0-9]+)*\z/', $name) !== 1
        || strlen($name) > 64
        || $name !== basename(dirname($path))
    ) {
        $errors[] = "{$path}: name must match its directory and the skill naming rules";
    }

    $description = $meta['description'] ?? '';

    $descriptionLength = is_string($description) ? mb_strlen(trim($description), 'UTF-8') : 0;

    if ($descriptionLength < 1 || $descriptionLength > 1024) {
        $errors[] = "{$path}: description must contain 1–1024 characters";
    }

    preg_match_all('/`([^`\n]*rules\/[a-z0-9-]+\.md)`/', $content, $references);

    foreach (array_unique($references[1]) as $reference) {
        if (is_file(dirname($path).'/'.$reference) === false) {
            $errors[] = "{$path}: missing bundled reference {$reference}";
        }
    }
}

if ($errors !== []) {
    fwrite(STDERR, implode(PHP_EOL, $errors).PHP_EOL);
    exit(1);
}

echo 'Validated '.count($skills).' skills and their bundled rule references.'.PHP_EOL;
