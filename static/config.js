/* 提示词模板 */
const promptTemplates = [
    {
        category: "动物",
        templates: [
            "一只可爱的橘猫坐在窗台上看风景",
            "一只威武的狼在月光下嚎叫",
            "一只色彩斑斓的蝴蝶停在花朵上",
            "一只优雅的天鹅在湖面上游动",
            "一只调皮的小狗在草地上玩耍"
        ]
    },
    {
        category: "美女",
        templates: [
            "全景图, 一个被日本传统麻绳缠绕, 倒挂在空中, 注意是倒挂在空中的裸体女性,麻绳交错，形成 ‘回旋纹’. 表情很魅惑和销魂,场景极具诱惑性. 双手被捆绑在身后, 下面有一桶水.模特身上有非常多的水!"
        ]
    },
    {
        category: "风景",
        templates: [
            "壮丽的日落映照在平静的海面上",
            "雪山之巅的壮丽景色",
            "樱花盛开的日本庭院",
            "北极光下的冰岛风光",
            "秋天的枫叶林"
        ]
    },
    {
        category: "城市",
        templates: [
            "赛博朋克风格的未来城市夜景",
            "繁华的东京街头夜景",
            "古老的欧洲小镇街道",
            "现代化的摩天大楼群",
            "威尼斯的水城风光"
        ]
    },
    {
        category: "人物",
        templates: [
            "一个穿着红色连衣裙的女孩在花园里",
            "一位老者在夕阳下钓鱼",
            "一个宇航员在太空中漂浮",
            "一位武士站在樱花树下",
            "一个小女孩抱着泰迪熊"
        ]
    },
    {
        category: "艺术",
        templates: [
            "梵高风格的星空",
            "水彩画风格的山水画",
            "油画风格的静物",
            "抽象艺术风格的色彩构成",
            "中国水墨画风格的竹林"
        ]
    },
    {
        category: "科幻",
        templates: [
            "外星球上的神秘建筑",
            "太空站内部的未来科技",
            "机器人在未来城市中行走",
            "星际飞船穿越虫洞",
            "外星生物的栖息地"
        ]
    }
];

/* 宽高比预设 */
const aspectRatios = {
    "1:1": { width: 1024, height: 1024, name: "正方形", icon: "⬜" },
    "2:3": { width: 1024, height: 1536, name: "竖屏", icon: "📱" },
    "3:2": { width: 1536, height: 1024, name: "横屏", icon: "🖼️" },
    "16:9": { width: 1792, height: 1024, name: "宽屏", icon: "🖥️" },
    "9:16": { width: 1024, height: 1792, name: "手机竖屏", icon: "📲" }
};

/* 快捷设置预设 */
const quickSettings = [
    {
        name: "社交媒体",
        aspectRatio: "1:1",
        count: 1,
        description: "适合 Instagram、微信朋友圈"
    },
    {
        name: "手机壁纸",
        aspectRatio: "9:16",
        count: 1,
        description: "适合手机竖屏壁纸"
    },
    {
        name: "电脑壁纸",
        aspectRatio: "16:9",
        count: 1,
        description: "适合电脑桌面壁纸"
    },
    {
        name: "批量创作",
        aspectRatio: "2:3",
        count: 4,
        description: "一次生成 4 张图片"
    }
];

/* 提示词优化建议 */
const promptTips = [
    "💡 添加具体的细节描述可以获得更好的效果",
    "🎨 指定艺术风格（如：油画、水彩、赛博朋克）",
    "🌈 描述色彩和光线（如：温暖的阳光、柔和的月光）",
    "📐 说明构图和视角（如：俯视、特写、全景）",
    "✨ 添加情感和氛围（如：宁静的、神秘的、欢快的）"
];

/* 常用关键词 */
const keywords = {
    style: ["油画", "水彩", "素描", "赛博朋克", "蒸汽朋克", "极简主义", "写实", "抽象"],
    lighting: ["日出", "日落", "月光", "霓虹灯", "柔和光线", "戏剧性光线", "背光"],
    mood: ["宁静", "神秘", "欢快", "忧郁", "梦幻", "史诗", "浪漫"],
    quality: ["高清", "4K", "超细节", "专业摄影", "电影级", "艺术品质"],
    camera: ["广角", "特写", "全景", "俯视", "仰视", "微距"]
};

/* 生成历史统计 */
const historyStats = {
    byCategory: {},
    byAspectRatio: {},
    byTime: {},
    popularPrompts: []
};

/* 导出配置 */
const exportFormats = [
    { name: "JSON", extension: "json", mime: "application/json" },
    { name: "CSV", extension: "csv", mime: "text/csv" },
    { name: "Markdown", extension: "md", mime: "text/markdown" }
];

/* 主题配置 */
const themes = {
    default: {
        name: "默认紫色",
        primary: "#667eea",
        secondary: "#764ba2",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    },
    blue: {
        name: "海洋蓝",
        primary: "#4facfe",
        secondary: "#00f2fe",
        background: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
    },
    pink: {
        name: "樱花粉",
        primary: "#f093fb",
        secondary: "#f5576c",
        background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
    },
    green: {
        name: "森林绿",
        primary: "#43e97b",
        secondary: "#38f9d7",
        background: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
    },
    orange: {
        name: "日落橙",
        primary: "#fa709a",
        secondary: "#fee140",
        background: "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
    }
};

/* 快捷操作 */
const shortcuts = {
    generate: "Ctrl+Enter",
    clear: "Ctrl+Shift+Delete",
    download: "Ctrl+S",
    fullscreen: "F11",
    help: "F1"
};

/* API 错误码映射 */
const errorMessages = {
    401: "认证失败，请检查 API Key",
    403: "访问被拒绝",
    404: "资源不存在",
    429: "请求过于频繁，请稍后再试",
    500: "服务器错误",
    502: "网关错误",
    503: "服务暂时不可用",
    504: "请求超时"
};

/* 性能监控 */
const performanceMetrics = {
    apiCalls: 0,
    successCount: 0,
    failureCount: 0,
    totalTime: 0,
    avgTime: 0,
    minTime: Infinity,
    maxTime: 0
};

/* 用户偏好设置 */
const userPreferences = {
    defaultAspectRatio: "2:3",
    defaultCount: 1,
    autoSave: true,
    showTips: true,
    theme: "default",
    language: "zh-CN"
};

/* 图片质量等级 */
const qualityLevels = {
    preview: { name: "预览", size: "~30KB", quality: 33 },
    medium: { name: "中等", size: "~100KB", quality: 66 },
    final: { name: "高清", size: ">100KB", quality: 99 }
};

/* 批量操作 */
const batchOperations = {
    downloadAll: "下载所有图片",
    deleteAll: "删除所有图片",
    exportHistory: "导出历史记录",
    importHistory: "导入历史记录"
};

/* 分享选项 */
const shareOptions = [
    { name: "复制链接", icon: "🔗" },
    { name: "下载图片", icon: "⬇️" },
    { name: "分享到社交媒体", icon: "📱" }
];

/* 过滤和排序选项 */
const filterOptions = {
    sortBy: ["时间", "宽高比", "提示词"],
    filterBy: ["全部", "今天", "本周", "本月"],
    aspectRatios: Object.keys(aspectRatios)
};

/* 帮助文档 */
const helpDocs = {
    gettingStarted: "快速开始指南",
    promptGuide: "提示词编写指南",
    apiReference: "API 参考文档",
    troubleshooting: "故障排查",
    faq: "常见问题"
};

/* 更新日志 */
const changelog = [
    {
        version: "1.0.0",
        date: "2026-02-03",
        changes: [
            "✨ 初始版本发布",
            "🎨 完整的图片生成界面",
            "📊 实时统计和进度显示",
            "💾 LocalStorage 数据持久化",
            "📱 响应式设计支持"
        ]
    }
];

/* 导出所有配置 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        promptTemplates,
        aspectRatios,
        quickSettings,
        promptTips,
        keywords,
        historyStats,
        exportFormats,
        themes,
        shortcuts,
        errorMessages,
        performanceMetrics,
        userPreferences,
        qualityLevels,
        batchOperations,
        shareOptions,
        filterOptions,
        helpDocs,
        changelog
    };
}
