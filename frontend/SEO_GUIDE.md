# SEO 和社交媒体配置指南

本文档说明了时序同笺项目中已实现的SEO和社交媒体优化功能。

## 已实现的功能

### 1. 基础SEO元标签

在 `BaseLayout.astro` 中实现：
- ✅ 页面标题 (title)
- ✅ 描述 (description)
- ✅ 关键词 (keywords)
- ✅ 作者信息 (author)
- ✅ Canonical URL
- ✅ Robots 指令
- ✅ 主题颜色

### 2. Open Graph 标签（Facebook/LinkedIn）

- ✅ og:type
- ✅ og:url
- ✅ og:title
- ✅ og:description
- ✅ og:image
- ✅ og:locale (支持多语言)
- ✅ og:site_name

### 3. Twitter 卡片标签

- ✅ twitter:card
- ✅ twitter:url
- ✅ twitter:title
- ✅ twitter:description
- ✅ twitter:image

### 4. 中国社交媒体优化

#### QQ分享
- ✅ itemprop (移动端)
- ✅ qq:title (PC端)
- ✅ qq:description
- ✅ qq:image

#### 微博分享
- ✅ weibo:title
- ✅ weibo:description
- ✅ weibo:image

#### 百度分享
- ✅ bdapp:title
- ✅ bdapp:description
- ✅ bdapp:image

### 5. 安全标头

- ✅ X-Content-Type-Options
- ✅ X-Frame-Options
- ✅ Referrer-Policy
- ✅ Permissions-Policy

### 6. 结构化数据 (Schema.org)

通过 `StructuredData.astro` 组件实现：
- ✅ JSON-LD 格式
- ✅ WebApplication 类型
- ✅ 应用信息（名称、描述、URL、图片）
- ✅ 价格信息（免费）

### 7. 其他SEO元素

- ✅ 语义化的 H1 标签（使用 sr-only 样式隐藏但对SEO友好）
- ✅ Favicon 支持
- ✅ robots.txt
- ✅ sitemap.xml

## 使用方法

### 在页面中使用

所有页面都继承自 `BaseLayout.astro`，可以自定义SEO属性：

\`\`\`astro
<BaseLayout 
  title="页面标题"
  description="页面描述"
  keywords="关键词1,关键词2,关键词3"
  image="/your-image.png"
  type="website"
  noindex={false}
>
  <!-- 添加SEO友好的h1标签 -->
  <h1 class="sr-only">页面主标题</h1>
  
  <!-- 页面内容 -->
</BaseLayout>
\`\`\`

### 配置说明

#### 必需配置

1. **Favicon**: 在 `frontend/public/` 目录下放置 `favicon.png` 文件
   - 推荐尺寸：512x512px
   - 格式：PNG（透明背景）

2. **网站URL**: 在 `astro.config.mjs` 中配置或设置环境变量
   \`\`\`javascript
   site: process.env.SITE_URL || 'http://localhost:4321'
   \`\`\`

3. **Sitemap**: 编辑 `frontend/public/sitemap.xml`，更新为实际域名

#### 可选配置

每个页面可以自定义以下属性：

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | string | 必填 | 页面标题 |
| description | string | "时序同笺..." | 页面描述 |
| keywords | string | "课表管理..." | SEO关键词 |
| author | string | "SDNU CS Team" | 作者 |
| image | string | "/favicon.png" | 分享图片 |
| url | string | 当前页面URL | 页面URL |
| type | string | "website" | Open Graph类型 |
| noindex | boolean | false | 是否阻止索引 |

## 部署前检查清单

- [ ] 替换 `public/favicon.png` 为实际图标
- [ ] 更新 `astro.config.mjs` 中的 `site` URL
- [ ] 更新 `public/sitemap.xml` 中的域名
- [ ] 检查所有页面的 title 和 description
- [ ] 测试社交媒体分享预览
  - Facebook: https://developers.facebook.com/tools/debug/
  - Twitter: https://cards-dev.twitter.com/validator
  - LinkedIn: https://www.linkedin.com/post-inspector/

## 测试工具

### 结构化数据测试
- Google 富媒体搜索结果测试：https://search.google.com/test/rich-results
- Schema.org 验证器：https://validator.schema.org/

### SEO分析
- Google PageSpeed Insights：https://pagespeed.web.dev/
- Google Search Console

### 社交媒体预览
- Facebook 调试工具：https://developers.facebook.com/tools/debug/
- Twitter 卡片验证器：https://cards-dev.twitter.com/validator
- LinkedIn 检查器：https://www.linkedin.com/post-inspector/

## 最佳实践

1. **标题优化**
   - 长度：50-60个字符
   - 包含主要关键词
   - 品牌名称放在末尾

2. **描述优化**
   - 长度：150-160个字符
   - 包含行动号召
   - 准确描述页面内容

3. **图片优化**
   - Open Graph 图片：1200x630px
   - Twitter 卡片：1200x675px
   - 文件大小：< 1MB
   - 格式：JPG 或 PNG

4. **关键词选择**
   - 3-5个核心关键词
   - 与页面内容高度相关
   - 考虑长尾关键词

## 维护建议

1. 定期检查 Google Search Console 的索引状态
2. 监控社交媒体分享数据
3. 根据用户反馈优化描述和关键词
4. 保持 sitemap.xml 更新
5. 定期测试结构化数据的有效性

## 技术栈

- **框架**: Astro 5.x
- **标准**: Open Graph Protocol, Schema.org
- **工具**: 结构化数据组件、SEO友好的HTML结构

