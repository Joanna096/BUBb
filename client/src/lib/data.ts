export type Availability = '平日早' | '平日中' | '平日晚' | '週末早' | '週末中' | '週末晚';
export type SkillType = '引導' | '行政' | '體力' | '臨場應變';

export interface Skill {
  type: SkillType;
  level: number; // 1-5
}

export interface HistoryRecord {
  id: string;
  eventName: string;
  role: string;
  date: string;
}

export interface Volunteer {
  id: string;
  name: string;
  phone: string;
  lineId: string;
  availability: Availability[];
  skills: Skill[];
  trustMetrics: {
    punctuality: number; // percentage
    taskCompletion: number; // 1-5
    reviews: number; // count of reviews
  };
  history: HistoryRecord[];
  avatar: string;
}

export const MOCK_VOLUNTEERS: Volunteer[] = [
  {
    id: '1',
    name: '陳小明',
    phone: '0912-345-678',
    lineId: 'ming_chen',
    availability: ['週末早', '週末中'],
    skills: [
      { type: '引導', level: 5 },
      { type: '體力', level: 3 }
    ],
    trustMetrics: {
      punctuality: 95,
      taskCompletion: 4.8,
      reviews: 12
    },
    history: [
      { id: 'h1', eventName: '2024 馬拉松', role: '路口引導', date: '2024-01-15' },
      { id: 'h2', eventName: '社區淨灘', role: '物資搬運', date: '2024-02-20' }
    ],
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix'
  },
  {
    id: '2',
    name: '林雅婷',
    phone: '0922-444-555',
    lineId: 'yating_lin',
    availability: ['平日晚', '週末晚'],
    skills: [
      { type: '行政', level: 5 },
      { type: '臨場應變', level: 4 }
    ],
    trustMetrics: {
      punctuality: 98,
      taskCompletion: 4.9,
      reviews: 25
    },
    history: [
      { id: 'h3', eventName: '慈善義賣', role: '收銀人員', date: '2023-12-10' }
    ],
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka'
  },
  {
    id: '3',
    name: '王大勇',
    phone: '0933-777-888',
    lineId: 'wang_hero',
    availability: ['平日早', '平日中', '平日晚'],
    skills: [
      { type: '體力', level: 5 },
      { type: '臨場應變', level: 2 }
    ],
    trustMetrics: {
      punctuality: 85,
      taskCompletion: 4.2,
      reviews: 8
    },
    history: [],
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Bob'
  },
  {
    id: '4',
    name: '張美玲',
    phone: '0911-222-333',
    lineId: 'meiling_chang',
    availability: ['週末早', '週末中', '週末晚'],
    skills: [
      { type: '引導', level: 4 },
      { type: '行政', level: 4 }
    ],
    trustMetrics: {
      punctuality: 92,
      taskCompletion: 4.5,
      reviews: 15
    },
    history: [
      { id: 'h4', eventName: '圖書館導覽', role: '導覽員', date: '2024-03-01' }
    ],
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Maria'
  }
];

export const SKILL_OPTIONS: SkillType[] = ['引導', '行政', '體力', '臨場應變'];
export const TIME_OPTIONS: Availability[] = ['平日早', '平日中', '平日晚', '週末早', '週末中', '週末晚'];
