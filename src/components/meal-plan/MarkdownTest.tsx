"use client";

import React from 'react';
import MarkdownRenderer from '@/components/ui/MarkdownRenderer';

const sampleMarkdown = `
# Weekly Meal Plan

## Monday
### Breakfast
- **Oatmeal** with *berries* and honey
- Green tea

### Lunch
| Food Item | Calories | Protein |
|-----------|----------|---------|
| Grilled Chicken Salad | 350 | 35g |
| Whole grain bread | 120 | 4g |
| Apple | 95 | 0.5g |

### Dinner
> "A healthy dinner is the foundation of good sleep and recovery."

## Tuesday
### Breakfast
\`\`\`javascript
const breakfast = {
  eggs: 2,
  toast: "whole wheat",
  avocado: "1/2 medium"
};
\`\`\`

### Snacks
1. **Greek yogurt** with honey
2. **Mixed nuts** (almonds, walnuts)
3. **Fresh fruits**

### Important Notes
- Drink **8 glasses** of water daily
- Exercise for *at least 30 minutes*
- Get **7-8 hours** of sleep
`;

export default function MarkdownTest() {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Markdown Rendering Test</h1>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <MarkdownRenderer 
          content={sampleMarkdown} 
          cacheKey="test-markdown"
        />
      </div>
    </div>
  );
}