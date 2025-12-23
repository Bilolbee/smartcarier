/**
 * =============================================================================
 * COMPANY HR DASHBOARD - Main Page
 * =============================================================================
 *
 * Features:
 * - Overview statistics
 * - Recent applications
 * - Active job postings
 * - AI Candidate recommendations
 * - Quick actions
 */

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Briefcase,
  Users,
  FileText,
  TrendingUp,
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  ArrowRight,
  PlusCircle,
  Star,
  Sparkles,
  Building2,
  Calendar,
  Mail,
  Phone,
  MapPin,
  ChevronRight,
  BarChart3,
  UserCheck,
  UserX,
  MessageSquare,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

// =============================================================================
// MOCK DATA - Replace with real API calls
// =============================================================================

const mockStats = {
  activeJobs: 5,
  totalApplications: 127,
  newApplications: 23,
  interviewScheduled: 8,
  hiredThisMonth: 3,
  averageTimeToHire: 14,
};

const mockRecentApplications = [
  {
    id: "1",
    candidateName: "Aziz Karimov",
    position: "Senior Software Engineer",
    appliedDate: "2024-01-15",
    status: "reviewing",
    matchScore: 92,
    avatar: null,
  },
  {
    id: "2",
    candidateName: "Dilnoza Rahimova",
    position: "Product Manager",
    appliedDate: "2024-01-14",
    status: "interview",
    matchScore: 87,
    avatar: null,
  },
  {
    id: "3",
    candidateName: "Jasur Toshmatov",
    position: "Senior Software Engineer",
    appliedDate: "2024-01-14",
    status: "new",
    matchScore: 78,
    avatar: null,
  },
  {
    id: "4",
    candidateName: "Malika Usmanova",
    position: "UX Designer",
    appliedDate: "2024-01-13",
    status: "offered",
    matchScore: 95,
    avatar: null,
  },
];

const mockActiveJobs = [
  {
    id: "1",
    title: "Senior Software Engineer",
    applications: 45,
    views: 230,
    daysActive: 7,
    status: "active",
  },
  {
    id: "2",
    title: "Product Manager",
    applications: 32,
    views: 180,
    daysActive: 14,
    status: "active",
  },
  {
    id: "3",
    title: "UX Designer",
    applications: 28,
    views: 150,
    daysActive: 5,
    status: "active",
  },
];

const mockAIRecommendations = [
  {
    id: "1",
    name: "Bobur Aliyev",
    title: "Full Stack Developer",
    matchScore: 96,
    skills: ["React", "Node.js", "Python", "AWS"],
    experience: "5 years",
    reason: "Perfect skill match for Senior Software Engineer role",
  },
  {
    id: "2",
    name: "Nodira Qodirova",
    title: "Product Lead",
    matchScore: 91,
    skills: ["Product Strategy", "Agile", "Data Analysis"],
    experience: "7 years",
    reason: "Strong leadership experience matches PM requirements",
  },
];

// =============================================================================
// COMPONENTS
// =============================================================================

const StatsCard = ({
  title,
  value,
  change,
  icon: Icon,
  color,
}: {
  title: string;
  value: string | number;
  change?: string;
  icon: any;
  color: string;
}) => (
  <Card>
    <CardContent className="pt-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-surface-500">{title}</p>
          <p className="mt-1 text-2xl font-bold text-surface-900 dark:text-white">
            {value}
          </p>
          {change && (
            <p className="mt-1 text-xs text-green-600 flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              {change}
            </p>
          )}
        </div>
        <div className={cn("flex h-12 w-12 items-center justify-center rounded-xl", color)}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </CardContent>
  </Card>
);

const StatusBadge = ({ status }: { status: string }) => {
  const configs: Record<string, { label: string; variant: string; icon: any }> = {
    new: { label: "New", variant: "bg-blue-100 text-blue-700", icon: Clock },
    reviewing: { label: "Reviewing", variant: "bg-yellow-100 text-yellow-700", icon: Eye },
    interview: { label: "Interview", variant: "bg-purple-100 text-purple-700", icon: Calendar },
    offered: { label: "Offered", variant: "bg-green-100 text-green-700", icon: CheckCircle },
    rejected: { label: "Rejected", variant: "bg-red-100 text-red-700", icon: XCircle },
  };

  const config = configs[status] || configs.new;

  return (
    <span className={cn("inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium", config.variant)}>
      <config.icon className="h-3 w-3" />
      {config.label}
    </span>
  );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function CompanyDashboardPage() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div {...fadeInUp} className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-surface-900 dark:text-white">
            Xush kelibsiz, {user?.company_name || "Kompaniya"} 👋
          </h1>
          <p className="mt-1 text-surface-500">
            HR Boshqaruv paneli - barcha nomzodlar va vakansiyalarni boshqaring
          </p>
        </div>
        <div className="flex gap-3">
          <Link href="/company/jobs/new">
            <Button variant="gradient">
              <PlusCircle className="mr-2 h-4 w-4" />
              Yangi vakansiya
            </Button>
          </Link>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        <StatsCard
          title="Faol vakansiyalar"
          value={mockStats.activeJobs}
          icon={Briefcase}
          color="bg-blue-100 dark:bg-blue-500/20 text-blue-600"
        />
        <StatsCard
          title="Jami arizalar"
          value={mockStats.totalApplications}
          change="+23 bu hafta"
          icon={FileText}
          color="bg-purple-100 dark:bg-purple-500/20 text-purple-600"
        />
        <StatsCard
          title="Suhbatga chaqirilgan"
          value={mockStats.interviewScheduled}
          icon={Calendar}
          color="bg-cyan-100 dark:bg-cyan-500/20 text-cyan-600"
        />
        <StatsCard
          title="Bu oy ishga olindi"
          value={mockStats.hiredThisMonth}
          icon={UserCheck}
          color="bg-green-100 dark:bg-green-500/20 text-green-600"
        />
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Applications */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-purple-500" />
                So'nggi arizalar
              </CardTitle>
              <Link href="/company/applicants">
                <Button variant="ghost" size="sm">
                  Barchasini ko'rish
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockRecentApplications.map((app, index) => (
                  <motion.div
                    key={app.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="flex items-center justify-between rounded-xl border border-surface-200 p-4 transition-all hover:border-purple-200 hover:bg-purple-50/50 dark:border-surface-700 dark:hover:border-purple-500/30 dark:hover:bg-purple-500/5"
                  >
                    <div className="flex items-center gap-4">
                      {/* Avatar */}
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 text-lg font-bold text-white">
                        {app.candidateName.split(" ").map((n) => n[0]).join("")}
                      </div>
                      <div>
                        <p className="font-semibold text-surface-900 dark:text-white">
                          {app.candidateName}
                        </p>
                        <p className="text-sm text-surface-500">{app.position}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {/* Match Score */}
                      <div className="text-right">
                        <div className="flex items-center gap-1 text-sm font-medium text-green-600">
                          <Sparkles className="h-4 w-4" />
                          {app.matchScore}% mos
                        </div>
                        <p className="text-xs text-surface-400">AI tahlil</p>
                      </div>
                      <StatusBadge status={app.status} />
                      <Link href={`/company/applicants/${app.id}`}>
                        <Button variant="ghost" size="sm">
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Active Jobs Sidebar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="h-5 w-5 text-blue-500" />
                Faol vakansiyalar
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {mockActiveJobs.map((job) => (
                <Link key={job.id} href={`/company/jobs/${job.id}`}>
                  <div className="rounded-xl border border-surface-200 p-4 transition-all hover:border-blue-200 hover:bg-blue-50/50 dark:border-surface-700 dark:hover:border-blue-500/30">
                    <p className="font-semibold text-surface-900 dark:text-white">
                      {job.title}
                    </p>
                    <div className="mt-2 flex items-center gap-4 text-sm text-surface-500">
                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        {job.applications}
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye className="h-4 w-4" />
                        {job.views}
                      </span>
                    </div>
                    <div className="mt-2">
                      <div className="flex items-center justify-between text-xs text-surface-400 mb-1">
                        <span>Arizalar</span>
                        <span>{job.applications}/50</span>
                      </div>
                      <Progress value={(job.applications / 50) * 100} className="h-1" />
                    </div>
                  </div>
                </Link>
              ))}
              <Link href="/company/jobs">
                <Button variant="outline" className="w-full">
                  Barchasi ko'rish
                </Button>
              </Link>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* AI Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              AI tavsiyalari
              <Badge className="ml-2 bg-purple-500 text-white">Yangi</Badge>
            </CardTitle>
            <p className="text-sm text-surface-500">
              AI tomonidan tanlangan eng mos nomzodlar
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {mockAIRecommendations.map((candidate, index) => (
                <motion.div
                  key={candidate.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 * index }}
                  className="rounded-xl border border-purple-200 bg-white p-4 shadow-sm dark:border-purple-500/30 dark:bg-surface-800"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 text-lg font-bold text-white">
                        {candidate.name.split(" ").map((n) => n[0]).join("")}
                      </div>
                      <div>
                        <p className="font-semibold text-surface-900 dark:text-white">
                          {candidate.name}
                        </p>
                        <p className="text-sm text-surface-500">{candidate.title}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 rounded-full bg-green-100 px-2 py-1 text-sm font-medium text-green-700">
                      <Star className="h-4 w-4 fill-current" />
                      {candidate.matchScore}%
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-surface-500">
                    <Sparkles className="mr-1 inline h-3 w-3 text-purple-500" />
                    {candidate.reason}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {candidate.skills.slice(0, 3).map((skill) => (
                      <Badge key={skill} variant="secondary" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                    {candidate.skills.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{candidate.skills.length - 3}
                      </Badge>
                    )}
                  </div>
                  <div className="mt-4 flex gap-2">
                    <Button size="sm" variant="gradient" className="flex-1">
                      <Mail className="mr-2 h-4 w-4" />
                      Bog'lanish
                    </Button>
                    <Button size="sm" variant="outline">
                      Profil
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        <Link href="/company/jobs/new">
          <Card className="cursor-pointer transition-all hover:border-purple-300 hover:shadow-lg">
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-100 text-purple-600 dark:bg-purple-500/20">
                <PlusCircle className="h-6 w-6" />
              </div>
              <div>
                <p className="font-semibold text-surface-900 dark:text-white">Vakansiya yaratish</p>
                <p className="text-sm text-surface-500">Yangi ish e'loni qo'shish</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/company/applicants">
          <Card className="cursor-pointer transition-all hover:border-blue-300 hover:shadow-lg">
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100 text-blue-600 dark:bg-blue-500/20">
                <Users className="h-6 w-6" />
              </div>
              <div>
                <p className="font-semibold text-surface-900 dark:text-white">Nomzodlar</p>
                <p className="text-sm text-surface-500">Arizalarni ko'rish</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/company/analytics">
          <Card className="cursor-pointer transition-all hover:border-cyan-300 hover:shadow-lg">
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-100 text-cyan-600 dark:bg-cyan-500/20">
                <BarChart3 className="h-6 w-6" />
              </div>
              <div>
                <p className="font-semibold text-surface-900 dark:text-white">Tahlil</p>
                <p className="text-sm text-surface-500">HR statistikasi</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/company/settings">
          <Card className="cursor-pointer transition-all hover:border-amber-300 hover:shadow-lg">
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100 text-amber-600 dark:bg-amber-500/20">
                <Building2 className="h-6 w-6" />
              </div>
              <div>
                <p className="font-semibold text-surface-900 dark:text-white">Kompaniya profili</p>
                <p className="text-sm text-surface-500">Ma'lumotlarni tahrirlash</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </motion.div>
    </div>
  );
}













